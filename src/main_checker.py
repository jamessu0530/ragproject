import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import ollama
from dotenv import load_dotenv
from utils.pinecone_utils import get_pinecone_index
from utils.embedding_utils import get_embedding
from utils.rerank_utils import rerank_documents
from utils.upsert_vectors import fetch_and_process_url
load_dotenv()
index = get_pinecone_index()
def search_and_answer(query: str):
    # 1. Search (Retrieve)
    query_vector = get_embedding(query, task_type="retrieval_query")
    results = index.query(
        vector=query_vector,
        top_k=20, # 抓多一點給 Cohere 挑
        include_metadata=True,
        namespace="web-check"
    )
    
    candidates = [m["metadata"]["text"] for m in results["matches"] if "text" in m["metadata"]]
    
    if not candidates:
        return "在這篇文章中找不到相關資訊。"
        
    # 2. Rerank (Cohere)
    print(f"正在使用 Cohere Rerank ({len(candidates)} 筆)...")
    ranked_results = rerank_documents(query, candidates, top_n=3)
    top_contexts = []
    for score, text in ranked_results:
        if score > 0.2: 
            top_contexts.append(text)
            
    context_text = "\n---\n".join(top_contexts)
    
    if not top_contexts:
        return "相關度太低，這篇文章可能沒有提到這個問題"

    # 3. Generate (Ollama)
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
        try:
            url = input("輸入網址 (輸入 q 離開)：").strip()
        except EOFError:
            break
            
        if url.lower() == 'q':
            break
        if fetch_and_process_url(url, namespace="web-check"):
            while True:
                try:
                    query = input("\n您想查詢什麼 (輸入 n 換網址, q 離開)：").strip()
                except EOFError:
                    break
                
                if query.lower() == 'q':
                    exit()
                if query.lower() == 'n':
                    break
                answer = search_and_answer(query)
                print("\n 回覆")
                print(answer)
