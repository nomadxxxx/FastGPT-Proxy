import os
import json
import time
import logging
import requests
from flask import Flask, request, Response
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# =========== Configuration ===========
# Environment variables should be set via Docker
KAGI_API_KEY = os.getenv('KAGI_API_KEY')
YOUR_API_KEY = os.getenv('API_KEY', 'dummy')  # Default to dummy key

# =========== Kagi API Client ===========
class KagiClient:
    def __init__(self):
        self.base_url = "https://kagi.com/api/v0/fastgpt"
        self.headers = {"Authorization": f"Bot {KAGI_API_KEY}"}

    def query(self, prompt: str) -> str:
        try:
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json={"query": prompt},
                timeout=15
            )
            response.raise_for_status()
            return response.json()["data"]["output"]
        except Exception as e:
            logger.error(f"Kagi API Error: {str(e)}")
            raise

# =========== OpenAI-Compatible Endpoints ===========
@app.route('/health', methods=['GET'])
def health_check():
    return {'status': 'ok'}, 200

@app.route('/v1/models', methods=['GET'])
def list_models():
    return {
        "object": "list",
        "data": [{
            "id": "fastgpt",
            "object": "model",
            "created": int(time.time()),
            "owned_by": "kagi"
        }]
    }

@app.route('/v1/chat/completions', methods=['POST'])
def chat_completion():
    # Authentication
    auth_header = request.headers.get("Authorization", "")
    if f"Bearer {YOUR_API_KEY}" not in auth_header:
        logger.warning(f"Invalid API key attempt from {request.remote_addr}")
        return {"error": "Unauthorized"}, 401

    # Process request
    try:
        payload = request.get_json()
        user_input = payload['messages'][-1]['content']
        
        client = KagiClient()
        full_response = client.query(user_input)
        
        return _stream_response(full_response)
        
    except Exception as e:
        logger.error(f"Request handling failed: {str(e)}")
        return {"error": str(e)}, 500

def _stream_response(content: str) -> Response:
    """Generate SSE response chunks."""
    chunks = [content[i:i+20] for i in range(0, len(content), 20)]
    timestamp = int(time.time())
    
    def generate():
        for idx, chunk in enumerate(chunks):
            yield json.dumps({
                "id": f"chatcmpl-{timestamp}-{idx}",
                "object": "chat.completion.chunk",
                "created": timestamp,
                "model": "fastgpt",
                "choices": [{
                    "delta": {"content": chunk},
                    "index": 0,
                    "finish_reason": "stop" if idx == len(chunks)-1 else None
                }]
            }) + "\n\n"
        yield "data: [DONE]\n\n"
    
    return Response(
        (f"data: {chunk}\n\n" for chunk in generate()),
        mimetype='text/event-stream',
        headers={'X-Accel-Buffering': 'no'}  # Disable NGINX buffering
    )

# =========== Entry Point ===========
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=False)
