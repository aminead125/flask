from flask import Flask, request, Response
import requests
import os

app = Flask(__name__)

@app.route('/')
def index():
    return "Proxy Render is running. Use /https://www.aliexpress.com/... to proxy."

@app.route('/<path:path>')
def proxy(path):
    if path.startswith('http'):
        url = path
    else:
        url = f"https://{path}"

    if request.query_string:
        url += f"?{request.query_string.decode()}"

    headers = {
        'Accept-Language': 'en-US,en;q=0.9',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
    }

    try:
        resp = requests.get(url, headers=headers, allow_redirects=True, timeout=20)
        return Response(resp.content, status=resp.status_code, content_type=resp.headers.get('content-type','text/html'))
    except Exception as e:
        return Response(f"Error fetching {url}: {e}", status=502)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
