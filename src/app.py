from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os
import logging

# 設定日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Vercel Serverless 環境的路徑處理
# 確保可以找到 NTOUutils 和 utils 模組
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)

# 添加多個可能的路徑
paths_to_add = [
    parent_dir,
    os.path.join(parent_dir, 'NTOUutils'),
    os.path.join(parent_dir, 'utils'),
]

for path in paths_to_add:
    if path not in sys.path:
        sys.path.insert(0, path)

# 延遲導入以避免在模組層級就失敗
# 在函數內部導入，這樣即使導入失敗也不會導致整個 app 無法啟動
def get_embedding_function():
    try:
        from NTOUutils.ntou_embedding import embed_and_upsert_products
        return embed_and_upsert_products
    except ImportError as e:
        logger.error(f"無法導入 embed_and_upsert_products: {e}")
        raise

def get_search_function():
    try:
        from NTOUutils.ntou_search import search_products
        return search_products
    except ImportError as e:
        logger.error(f"無法導入 search_products: {e}")
        raise

# 在模組層級嘗試導入（用於健康檢查）
try:
    from NTOUutils.ntou_embedding import embed_and_upsert_products
    from NTOUutils.ntou_search import search_products
    logger.info("模組導入成功")
except ImportError as e:
    logger.warning(f"模組導入失敗（將在運行時重試）: {e}")
    logger.warning(f"sys.path: {sys.path}")
    logger.warning(f"current_dir: {current_dir}")
    logger.warning(f"parent_dir: {parent_dir}")
    # 不 raise，讓 app 先啟動，在實際使用時再處理

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
        # 運行時導入，確保路徑正確
        try:
            from NTOUutils.ntou_embedding import embed_and_upsert_products
        except ImportError:
            embed_and_upsert_products = get_embedding_function()
        
        logger.info("開始更新產品向量資料庫...")
        embed_and_upsert_products()
        logger.info("產品向量資料庫更新完成")
        return jsonify({"status": "success", "message": "產品向量資料庫更新完成"}), 200
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        logger.error(f"資料庫更新失敗: {e}\n{error_detail}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/search', methods=['POST'])
def search():
    """
    接收 { "query": "使用者問題" }
    回傳搜尋結果 JSON (產品 ID 列表)
    """
    try:
        data = request.json
        if not data or 'query' not in data:
            return jsonify({"status": "error", "message": "Missing 'query' field"}), 400
        
        query_text = data['query']
        logger.info(f"收到搜尋請求: {query_text}")
        
        # 檢查環境變數
        required_env = ['PINECONE_API_KEY', 'PINECONE_INDEX', 'GOOGLE_API_KEY']
        missing_env = [key for key in required_env if not os.getenv(key)]
        if missing_env:
            logger.error(f"缺少環境變數: {missing_env}")
            return jsonify({"status": "error", "message": f"Missing environment variables: {', '.join(missing_env)}"}), 500
        
        # 運行時導入，確保路徑正確
        try:
            from NTOUutils.ntou_search import search_products
        except ImportError:
            search_products = get_search_function()
        
        results = search_products(query_text)
        id_list = [item['id'] for item in results]
        logger.info(f"搜尋完成，找到 {len(id_list)} 筆結果")
        return jsonify(id_list), 200
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        logger.error(f"搜尋失敗: {e}\n{error_detail}")
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
