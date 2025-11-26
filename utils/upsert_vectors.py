import sys
import os
import time
import hashlib
from utils.pinecone_utils import get_pinecone_index
from utils.embedding_utils import get_embedding
from utils.crawler_utils import fetch_url_content
from utils.chunking_utils import split_text_into_chunks
index = get_pinecone_index()
def get_url_hash(url: str) -> str:
    return hashlib.md5(url.encode()).hexdigest()
def fetch_and_process_url(url, namespace):
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
        print("內容太短跳過儲存")
        return False
    # 3. 存入 Pinecone
    url_hash = get_url_hash(url)
    vectors = []
    for idx, chunk in enumerate(chunks):#爲chunk 加上索引值
        unique_id = f"{url_hash}_{idx}"#chunk 的唯一id
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
    print(f"寫入 {len(vectors)} 筆資料到 namespace='{namespace}' (ID prefix: {url_hash})")
    
    # 等待索引生效
    time.sleep(2) 
    return True
