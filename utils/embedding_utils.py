import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
def get_embedding(text: str):
    try:
        # 'models/text-embedding-004' 是目前建議的模型，維度 768
        result = genai.embed_content(
            model="models/text-embedding-004",
            content=text,
            task_type="retrieval_document",
        )
        return result['embedding']
    except Exception as e:
        print(f"Embedding failed: {e}")
        return []

