import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import ollama
from dotenv import load_dotenv
from utils.pinecone_utils import get_pinecone_index
from utils.embedding_utils import get_embedding
from utils.rerank_utils import rerank_documents
from utils.pdf_utils import fetch_and_process_pdf, fetch_and_process_pdf_folder
load_dotenv()
index = get_pinecone_index()
def search_and_answer(query: str):
    # 1. Search (Retrieve) 檢索
    query_vector = get_embedding(query, task_type="retrieval_query")#問問題有自己的task_typet傳給genai
    results = index.query(
        vector=query_vector,
        top_k=20, # 抓多一點給 Cohere 挑，index query 是 pinecone 的 query ，top_k 是回傳的結果數量
        include_metadata=True,
        namespace="web-check"
    )
    print(f"Pinecone 搜尋結果：找到 {len(results['matches'])} 筆資料")
    for m in results["matches"]:
        print(m["id"], m["score"])#檢查 pinecone 的 query 結果
    
    candidates = [m["metadata"]["text"] for m in results["matches"] if "text" in m["metadata"]]   
        
    # 2. Rerank (Cohere)
    print(f"Cohere Rerank ({len(candidates)} 筆)")
    ranked_results = rerank_documents(query, candidates, top_n=3)
    top_contexts = []
    for score, text in ranked_results:
        if score > 0.2: 
            top_contexts.append(text)
            
    context_text = "\n---\n".join(top_contexts)#只是給三個chunk 之間有間隔
    
    if not top_contexts:
        msg = "相關度太低，這篇文章可能沒有提到這個問題"
        print(msg)
        return msg

    # 3. Generate (Ollama)
    prompt = f"""你是一個專業的事實查核員。請根據以下【文章片段】來回答使用者的問題。
請用繁體中文回答。如果文章中沒有提到相關資訊，請直接說「文章中未提及」。
【文章片段】：
{context_text}

【使用者問題】：
{query}

【查核結果】：
"""
    
    stream = ollama.chat(model='gemma3:4b', messages=[{'role': 'user', 'content': prompt}], stream=True)
    
    full_response = ""
    for chunk in stream:
        content = chunk['message']['content']
        print(content, end='' , flush=True)
        full_response += content
        
    print("\n")
    return full_response

if __name__ == "__main__":
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    pdfs_folder = os.path.join(project_root, "pdfs")
    
    # 直接讀取 pdfs 資料夾
    print("正在讀取 pdfs 資料夾中的所有 PDF 檔案...")
    fetch_and_process_pdf_folder(pdfs_folder, namespace="web-check")
    
    # 詢問查詢問題
    try:
        query = input("\n您想查詢什麼：").strip()
        if query:
            search_and_answer(query)
    except (EOFError, KeyboardInterrupt):
        print("\n程式已結束")
