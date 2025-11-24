import sys
import os
import time
import hashlib

# 讓這個檔案可以直接執行
if __name__ == "__main__":
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.pinecone_utils import get_pinecone_index
from utils.embedding_utils import get_embedding
from utils.crawler_utils import fetch_url_content
from utils.chunking_utils import split_text_into_chunks

# 初始化 Pinecone
# 注意：如果被 import 使用，這裡會直接執行，這是預期行為
index = get_pinecone_index()

def get_url_hash(url: str) -> str:
    """
    產生 URL 的 MD5 hash，作為 ID 前綴
    """
    return hashlib.md5(url.encode()).hexdigest()

def fetch_and_process_url(url: str, namespace: str = "web-check"):
    """
    1. 抓取網頁 (Crawler)
    2. 切片 (Chunking)
    3. 存入 Pinecone (Upsert)
    """
    # 1. 抓取
    text = fetch_url_content(url)
    if not text:
        return False

    # 2. 切片
    chunks = split_text_into_chunks(text)
    if not chunks:
        print("⚠️ 網頁內容過短或無法解析，跳過儲存。")
        return False

    # 3. 存入 Pinecone
    url_hash = get_url_hash(url)
    vectors = []
    
    for idx, chunk in enumerate(chunks):
        unique_id = f"{url_hash}_{idx}"
        
        vector = {
            "id": unique_id,
            "values": get_embedding(chunk),
            "metadata": {
                "text": chunk,
                "url": url,
                "chunk_index": idx
            }
        }
        vectors.append(vector)
    
    # 批次寫入
    batch_size = 100
    for i in range(0, len(vectors), batch_size):
        batch = vectors[i:i+batch_size]
        index.upsert(vectors=batch, namespace=namespace)
        
    print(f"💾 成功寫入 {len(vectors)} 筆資料到 namespace='{namespace}' (ID prefix: {url_hash})")
    
    # 等待索引生效
    time.sleep(2) 
    return True

if __name__ == "__main__":
    url = input("🌐 請輸入要抓取的網址：").strip()
    if url:
        fetch_and_process_url(url)
