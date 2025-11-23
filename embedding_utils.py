import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# 設定 Google API Key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def get_embedding(text: str):
    """
    使用 Google Gemini text-embedding-004 模型產生向量 (維度 768)
    """
    try:
        # 'models/text-embedding-004' 是目前建議的模型，維度 768
        result = genai.embed_content(
            model="models/text-embedding-004",
            content=text,
            task_type="retrieval_document",
            title="Embedding of single string"
        )
        return result['embedding']
    except Exception as e:
        print(f"❌ Embedding 生成失敗: {e}")
        return []

