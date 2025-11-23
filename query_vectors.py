import os
from dotenv import load_dotenv
from pinecone import Pinecone
from embedding_utils import get_embedding

load_dotenv()
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index(os.getenv("PINECONE_INDEX"))

query = "請輸入你想搜尋的關鍵字"
res = index.query(
    vector=get_embedding(query), # 改用 Google Embedding
    top_k=3,
    include_metadata=True,
    namespace="default"
)

for m in res["matches"]:
    print(f"- {m['id']} score={m['score']:.4f} text={m['metadata'].get('text', 'No text')}")
