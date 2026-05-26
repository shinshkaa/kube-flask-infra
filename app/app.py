import os
import time
from flask import Flask, jsonify
from prometheus_client import make_wsgi_app, Counter, Histogram
from werkzeug.middleware.dispatcher import DispatcherMiddleware

app = Flask(__name__)

REQUEST_COUNT = Counter('app_requests_total', 'Total number of requests', ['method', 'endpoint', 'http_status'])
REQUEST_LATENCY = Histogram('app_request_latency_seconds', 'Application response latency')

@app.before_request
def start_timer():
    import time
    from flask import g
    g.start_time = time.time()

@app.after_request
def log_request(response):
    if hasattr(response, 'status_code') and hasattr(response, 'headers'):
        from flask import request
        if request.path not in ['/health', '/metrics']:
            latency = time.time() - getattr(Flask, 'start_time', time.time())
            REQUEST_COUNT.labels(method=request.method, endpoint=request.path, http_status=response.status_code).inc()
    return response

@app.route('/')
def index():
    app_mode = os.getenv('APP_MODE', 'development')
    api_key = os.getenv('API_KEY', 'not-set')
    
    return jsonify({
        "message": "Hello from Kubernetes!",
        "mode": app_mode,
        "api_key_configured": api_key != 'not-set'
    })

@app.route('/health')
def health():
    return jsonify({"status": "UP"}), 200

app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
    '/metrics': make_wsgi_app()
})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)