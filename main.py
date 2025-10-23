from flask import Flask, request, Response, jsonify
import requests
import os

app = Flask(__name__)

# Configuration
TIMEOUT = 30
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0'
]

@app.route('/')
def home():
    return """
    <h1>✅ Proxy AliExpress Actif</h1>
    <p>Usage: /get?url=https://www.aliexpress.com/item/...</p>
    <br>
    <a href="/test">Test avec un produit</a>
    """

@app.route('/test')
def test():
    """Route de test"""
    test_url = "https://www.aliexpress.com/item/1005003339741426.html"
    return proxy_get(test_url)

@app.route('/get')
def proxy_get(target_url=None):
    """Proxy GET amélioré"""
    
    if not target_url:
        target_url = request.args.get('url')
    
    if not target_url:
        return jsonify({"error": "No URL provided"}), 400
    
    try:
        # Headers complets pour éviter la détection
        headers = {
            'User-Agent': USER_AGENTS[0],
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
            'Cookie': 'aep_usuc_f=site=glo&c_tp=USD&region=US&b_locale=en_US; intl_locale=en_US; xman_us_f=x_locale=en_US'
        }
        
        # Session pour cookies persistants
        with requests.Session() as session:
            session.headers.update(headers)
            
            # Faire la requête
            response = session.get(
                target_url,
                timeout=TIMEOUT,
                allow_redirects=True,
                verify=True
            )
            
            # Log pour debug
            print(f"Proxied: {target_url[:50]}... -> {response.status_code}")
            
            # Créer la réponse
            excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
            headers_dict = {
                k: v for k, v in response.headers.items()
                if k.lower() not in excluded_headers
            }
            
            return Response(
                response.content,
                status=response.status_code,
                headers=headers_dict
            )
            
    except requests.Timeout:
        return jsonify({"error": "Timeout"}), 504
    except requests.RequestException as e:
        print(f"Request error: {e}")
        return jsonify({"error": str(e)}), 502
    except Exception as e:
        print(f"Unexpected error: {e}")
        return jsonify({"error": "Internal error"}), 500

# Route alternative pour compatibilité
@app.route('/<path:path>')
def proxy_path(path):
    """Route avec path direct"""
    
    # Construire l'URL complète
    if path.startswith('http'):
        target_url = path
    else:
        target_url = f"https://www.aliexpress.com/{path}"
    
    # Ajouter query string
    if request.query_string:
        target_url += f"?{request.query_string.decode()}"
    
    return proxy_get(target_url)

@app.route('/proxy')
def proxy_route():
    """Route /proxy pour compatibilité"""
    return proxy_get()

@app.route('/health')
def health():
    """Health check"""
    return jsonify({"status": "healthy"}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
