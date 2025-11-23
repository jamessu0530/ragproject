# create_index.py
import os
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec

load_dotenv()
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

index_name = os.getenv("PINECONE_INDEX", "medical-fact-checker")

# 若已存在就略過
existing = [i.name for i in pc.list_indexes()]
if index_name not in existing:
    pc.create_index(
        name=index_name,
        dimension=768,             # Gemini Embedding 維度
        metric="cosine",           # 與 normalize 後的向量相容
        spec=ServerlessSpec(
            cloud="aws",           # 依你要的區域
            region="us-east-1"     # 常見區域：us-east-1 / us-west-2
        )
    )
    print("Index created:", index_name)
else:
    print("Index already exists:", index_name)
