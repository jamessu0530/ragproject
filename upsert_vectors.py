import os
from dotenv import load_dotenv
from pinecone import Pinecone
from embedding_utils import get_embedding

load_dotenv()
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index(os.getenv("PINECONE_INDEX"))

# 準備真實資料
docs = [
    # 格式範例：
    # ("id_1", "這是一段真實的資料..."),
]

if not docs:
    print("⚠️ 目前沒有資料可以上傳，請先編輯 docs 列表。")
else:
    # upsert 到 Pinecone
    vectors = []
    for _id, text in docs:
        vectors.append({
            "id": _id, 
            "values": get_embedding(text), # 改用 Google Embedding
            "metadata": {"text": text}
        })
    
    index.upsert(vectors=vectors, namespace="default")
    print(f"✅ 成功上傳 {len(docs)} 筆資料！")
