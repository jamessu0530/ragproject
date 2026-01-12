import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

# 只在環境變數不存在時才載入預設 .env（不覆蓋已載入的環境變數）
if not os.getenv("GOOGLE_API_KEY"):
    load_dotenv()

# 初始化 client
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

def get_embedding(text: str, task_type: str = "RETRIEVAL_DOCUMENT"): # 預設適用於存資料庫
    """
    使用 Google Gemini API 生成文字 embedding
    
    Args:
        text: 要轉換為 embedding 的文字
        task_type: 任務類型，可選值:
            - RETRIEVAL_DOCUMENT: 用於儲存文件（預設）
            - RETRIEVAL_QUERY: 用於搜尋查詢
            - SEMANTIC_SIMILARITY: 用於語意相似度
    """
    try:
        result = client.models.embed_content(
            model="text-embedding-004",
            contents=[text],
            config=types.EmbedContentConfig(task_type=task_type)
        )
        return result.embeddings[0].values
    except Exception as e:
        print(f"Embedding failed: {e}")
        return None  # 空字串無法被 embedding
