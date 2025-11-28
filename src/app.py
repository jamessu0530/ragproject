from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os
import logging

# 設定日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 加入根目錄以便匯入
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from NTOUutils.ntou_embedding import embed_and_upsert_products
from NTOUutils.ntou_search import search_products

app = Flask(__name__)

# CORS 設定：生產環境建議限制特定網域
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*")  # 預設允許所有，生產環境建議設定特定網域
if CORS_ORIGINS != "*":
    CORS(app, origins=CORS_ORIGINS.split(","))
else:
    CORS(app)

# 健康檢查端點
@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy"}), 200

@app.route('/api/init', methods=['POST'])
def init_db():
    """
    手動觸發資料庫更新 (Embedding & Upsert)
    """
    try:
        logger.info("開始更新產品向量資料庫...")
        embed_and_upsert_products()
        logger.info("產品向量資料庫更新完成")
        return jsonify({"status": "success", "message": "產品向量資料庫更新完成"}), 200
    except Exception as e:
        logger.error(f"資料庫更新失敗: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/search', methods=['POST'])
def search():
    """
    接收 { "query": "使用者問題" }
    回傳搜尋結果 JSON (產品 ID 列表)
    """
    data = request.json
    if not data or 'query' not in data:
        return jsonify({"status": "error", "message": "Missing 'query' field"}), 400
    
    query_text = data['query']
    
    try:
        logger.info(f"收到搜尋請求: {query_text}")
        results = search_products(query_text)
        id_list = [item['id'] for item in results]
        logger.info(f"搜尋完成，找到 {len(id_list)} 筆結果")
        return jsonify(id_list), 200
    except Exception as e:
        logger.error(f"搜尋失敗: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

# Vercel 需要將 app 作為 module 導出
# 本地開發時才執行啟動邏輯
if __name__ == '__main__':
    PORT = int(os.getenv("PORT", 5001))
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    AUTO_INIT = os.getenv("AUTO_INIT", "True").lower() == "true"
    
    if AUTO_INIT:
        logger.info(">>> 伺服器啟動，正在初始化產品資料庫...")
        try:
            embed_and_upsert_products()
            logger.info(">>> 初始化完成")
        except Exception as e:
            logger.error(f"初始化失敗: {e}")
            logger.warning(">>> 將繼續啟動，但資料庫可能未更新")
    
    logger.info(f">>> API 服務啟動於 port {PORT} (DEBUG={DEBUG})")
    app.run(host='0.0.0.0', port=PORT, debug=DEBUG)
