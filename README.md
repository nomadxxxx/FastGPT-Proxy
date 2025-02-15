# FastGPT Proxy: Project Overview
### 1. What is FastGPT Proxy?
FastGPT Proxy is a lightweight proxy allowing FastGPT API to be OpenAI-compatible. This allows FastGPT(ChatGPT 4o varient) to be used as a model in services like [Open WebUI](https://github.com/open-webui/open-webui) which provides STT and TTS, letting you use the 'call' and 'record to send' functions (this is currently unvailable on default FastGPT portal).
### 2. Technical Stack  
| Component          | Technology                              | Purpose                                  |
|--------------------|-----------------------------------------|------------------------------------------|
| Core Language      | Python 3.11                             | Backend logic and API handling           |
| Web Framework      | Flask 3.0                               | HTTP request routing and response        |
| Production WSGI    | Gunicorn 21.2                           | Scalable server for production use       |
| Dependencies       | requests, flask-cors, python-dotenv     | HTTP calls, CORS, environment variables  |
| Deployment         | Docker, GitHub Container Registry (GHCR)| Containerization and distribution        |

### 3. Key Objectives  

✅ OpenAI API Compatibility : Kagi FastGPT responses into OpenAI’s /v1/chat/completions format for drop-in replacement.

✅ Self-Hosted Alternative : Lets you use FastGPT with TTS and STT functionality provided by Open WebUI including open calls.

✅ Simplified Integration : Single Docker image with minimal setup steps.

### 4. Limitations  
Functional Constraints  
- No Streaming Support : Responses are delivered as a single block (no real-time chunks).  
- Basic Error Handling : Errors from Kagi API may not be fully translated to OpenAI format.   
- Optional Parameter Support : Not all OpenAI parameters (e.g., temperature, top_p) etc.
     
### 5. Future Enhancements  
- If Kagi decides to offer the models they already offer in with their Kagi Assistant, I will develop a model pull script like what OpenWeb UI provides for OpenRouter: see https://openwebui.com/t/yikesawjeez/yikes_openrouter
- Streaming Support : SSE (Server-Sent Events) for real-time text generation.  

     
### 7. Quick Start (TL;DR)  
Deploy with Docker  
```shell
docker run -d --name fastgpt-proxy -p 5000:5000 \
  -e KAGI_API_KEY=your_kagi_api_key_here \
  -e API_KEY=your_optional_api_key_here \
  ghcr.io/nomadxxxx/fastgpt-proxy:latest
```
Then configure Open WebUI to use http://localhost:5000/v1 as the OpenAI endpoint.   

## The harder way
Clone repository:
```shell
git clone https://github.com/nomadxxxx/fastgpt-proxy.git
cd fastgpt-proxy
```
Create virtual environment:
```shell
python3 -m venv venv
source venv/bin/activate  # Linux/Mac | venv\Scripts\activate for Windows
```
Install dependencies
```shell
pip install -r requirements.txt
```
Configure .env file
```shell
.env
```
nano .env  # Edit KAGI_API_KEY and optional API_KEY

Start server
```shell
python3 app/server.py
```
Note you can also you:
```gunicorn --bind 0.0.0.0:5000 app.server:app```

