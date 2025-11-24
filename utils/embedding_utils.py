import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def get_embedding(text: str, task_type: str = "retrieval_document"):#預設適用於存資料庫
    try:
        result = genai.embed_content(
            model="models/text-embedding-004",
            content=text,
            task_type=task_type,#如果是使用者問題會改成retrieval_query
        )
        return result['embedding']
    except Exception as e:
        print(f"Embedding failed: {e}")
        return None #空字串無法被embedding

