import os
from dotenv import load_dotenv
from pinecone import Pinecone

# 只在環境變數不存在時才載入預設 .env（不覆蓋已載入的環境變數）
if not os.getenv("PINECONE_INDEX"):
    load_dotenv()

def get_pinecone_index():
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    index_name = os.getenv("PINECONE_INDEX")
    return pc.Index(index_name)

