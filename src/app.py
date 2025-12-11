from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os

# 加入根目錄以便匯入模組
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from NTOUutils.ntou_search import search_products

app = Flask(__name__)
CORS(app)

@app.route('/api/search', methods=['POST'])
def search():
    """搜尋產品"""
    try:
        data = request.json
        if not data or 'query' not in data:
            return jsonify({"error": "Missing 'query' field"}), 400
        
        results = search_products(data['query'])
        id_list = [item['id'] for item in results]
        return jsonify(id_list), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv("PORT", 5001)))
