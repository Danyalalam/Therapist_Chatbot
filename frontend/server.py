# frontend/server.py
from flask import Flask, send_from_directory, request, jsonify
from flask_cors import CORS
import requests
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder='static')
CORS(app)

@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

@app.route('/chat', methods=['POST'])
def chat():
    try:
        logger.debug(f"Received request: {request.json}")
        response = requests.post(
            'http://localhost:8000/chat',
            headers={'Content-Type': 'application/json'},
            json=request.json,
            timeout=30
        )
        logger.debug(f"Backend response: {response.text}")
        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        logger.error(f"Backend error: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)