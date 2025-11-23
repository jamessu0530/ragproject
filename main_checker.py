import os
import time
import requests
import ollama
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from pinecone import Pinecone
from sentence_transformers import CrossEncoder
from embedding_utils import get_embedding

# 載入環境變數
load_dotenv()

# 初始化 Pinecone
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index(os.getenv("PINECONE_INDEX"))

# 初始化 Rerank 模型 (Embedding 改用 Google API，不需在此載入)
print("📥 正在載入 Rerank 模型...")
rerank_model = CrossEncoder("BAAI/bge-reranker-base", max_length=512)
print("✅ 模型載入完成！")

def fetch_and_process_url(url: str):
    """
    1. 抓取網頁
    2. 提取文字
    3. 切片 (Chunking)
    4. 存入 Pinecone (namespace='web-check')
    """
    print(f"🕷️  正在抓取網址：{url} ...")
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
    except Exception as e:
        print(f"❌ 抓取失敗：{e}")
        return False

    soup = BeautifulSoup(resp.text, "html.parser")
    
    # 移除 script 和 style
    for script in soup(["script", "style", "nav", "footer"]):
        script.extract()
        
    text = soup.get_text(separator="\n")
    
    # --- 簡單的切片策略 (Chunking) ---
    lines = [line.strip() for line in text.split('\n') if len(line.strip()) > 20]
    
    chunks = []
    for i in range(0, len(lines), 3):
        chunk = " ".join(lines[i:i+3])
        chunks.append(chunk)
        
    print(f"🔪 已切分為 {len(chunks)} 個片段，準備存入資料庫...")

    # --- 存入 Pinecone ---
    vectors = []
    for idx, chunk in enumerate(chunks):
        safe_chunk = chunk[:30000] 
        vector = {
            "id": f"web_{idx}",
            "values": get_embedding(safe_chunk), # 改用 Google Embedding
            "metadata": {"text": safe_chunk}
        }
        vectors.append(vector)
    
    # 批次寫入
    batch_size = 100
    for i in range(0, len(vectors), batch_size):
        batch = vectors[i:i+batch_size]
        index.upsert(vectors=batch, namespace="web-check")
        
    print(f"💾 成功寫入 {len(vectors)} 筆資料到 namespace='web-check'")
    
    time.sleep(2) 
    return True

def search_and_answer(query: str):
    """
    RAG 流程：Search -> Rerank -> Generate
    """
    print(f"🔍 正在文章中搜尋：{query}")
    
    # 1. Search
    query_vector = get_embedding(query) # 改用 Google Embedding
    results = index.query(
        vector=query_vector,
        top_k=15,
        include_metadata=True,
        namespace="web-check"
    )
    
    candidates = [m["metadata"]["text"] for m in results["matches"] if "text" in m["metadata"]]
    
    if not candidates:
        return "❌ 在這篇文章中找不到相關資訊。"
        
    # 2. Rerank
    pairs = [[query, doc] for doc in candidates]
    scores = rerank_model.predict(pairs)
    ranked_results = sorted(zip(scores, candidates), key=lambda x: x[0], reverse=True)
    
    # 取 Top 3
    top_contexts = [text for score, text in ranked_results[:3] if score > -10]
    context_text = "\n---\n".join(top_contexts)
    
    if not top_contexts:
        return "❌ 相關度太低，這篇文章可能沒有提到這個問題。"

    # 3. Generate
    print("🤖 正在閱讀相關段落並生成回答...")
    prompt = f"""你是一個專業的事實查核員。請根據以下【文章片段】來回答使用者的問題。
請用繁體中文回答。如果文章中沒有提到相關資訊，請直接說「文章中未提及」。

【文章片段】：
{context_text}

【使用者問題】：
{query}

【查核結果】：
"""
    
    response = ollama.chat(model='gemma3:4b', messages=[{'role': 'user', 'content': prompt}])
    return response['message']['content']

if __name__ == "__main__":
    while True:
        print("\n" + "="*50)
        try:
            url = input("🌐 請輸入網址 (輸入 q 離開)：").strip()
        except EOFError:
            break
            
        if url.lower() == 'q':
            break
            
        if fetch_and_process_url(url):
            while True:
                try:
                    query = input("\n❓ 您想查詢什麼 (輸入 n 換網址, q 離開)：").strip()
                except EOFError:
                    break
                
                if query.lower() == 'q':
                    exit()
                if query.lower() == 'n':
                    break
                
                answer = search_and_answer(query)
                print("\n📝 回答：")
                print(answer)
