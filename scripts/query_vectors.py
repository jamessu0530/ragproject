import sys
import os

# 將專案根目錄加入 sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.pinecone_utils import get_pinecone_index
from utils.embedding_utils import get_embedding

# 初始化 Pinecone
index = get_pinecone_index()

query = "請輸入你想搜尋的關鍵字"
res = index.query(
    vector=get_embedding(query),
    top_k=3,
    include_metadata=True,
    namespace="default"
)

for m in res["matches"]:
    print(f"- {m['id']} score={m['score']:.4f} text={m['metadata'].get('text', 'No text')}")
