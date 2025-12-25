# create_rag_project_index.py
# 創建名為 rag-project 的 Pinecone 向量資料庫索引
import os
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec

load_dotenv()
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

index_name = "rag-project"

# 檢查是否已存在
existing = [i.name for i in pc.list_indexes()]
print(f"現有的 indexes: {existing}")

if index_name not in existing:
    print(f"正在創建索引 '{index_name}'...")
    pc.create_index(
        name=index_name,
        dimension=768,             # Google Gemini text-embedding-004 維度
        metric="cosine",           # 餘弦相似度
        spec=ServerlessSpec(
            cloud="aws",           # AWS 雲端
            region="us-east-1"     # 美國東部區域
        )
    )
    print(f"✅ 成功創建索引: {index_name}")
    print(f"   - Dimension: 768")
    print(f"   - Metric: cosine")
    print(f"   - Cloud: AWS")
    print(f"   - Region: us-east-1")
else:
    print(f"ℹ️  索引 '{index_name}' 已存在，無需創建。")
