import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import ollama
from dotenv import load_dotenv
from utils.pinecone_utils import get_pinecone_index
from utils.embedding_utils import get_embedding
from utils.rerank_utils import rerank_documents
from utils.pdf_utils import fetch_and_process_pdf, fetch_and_process_pdf_folder

# 載入環境變數
load_dotenv()
index = get_pinecone_index()

def search_and_answer(query: str):
    # 1. Search (Retrieve) 檢索 - 直接用中文查詢
    query_vector = get_embedding(query, task_type="retrieval_query")
    results = index.query(
        vector=query_vector,
        top_k=20,
        include_metadata=True,
        namespace="web-check"
    )
    print(f"Pinecone 搜尋結果：找到 {len(results['matches'])} 筆資料")
    for m in results["matches"]:
        print(m["id"], m["score"])
    
    candidates = [m["metadata"]["text"] for m in results["matches"] if "text" in m["metadata"]]   
        
    # 2. Rerank (Cohere) - 用中文查詢
    rerank_query = query
    
    print(f"Cohere Rerank ({len(candidates)} 筆)")
    ranked_results = rerank_documents(rerank_query, candidates, top_n=3)
    
    # Debug: 顯示 rerank 分數
    print("Rerank 分數：", [f"{score:.4f}" for score, _ in ranked_results])
    
    top_contexts = []
    for score, text in ranked_results:
        if score >= 0.1:  # 相關度 0.1 以上就使用
            top_contexts.append(text)
            
    context_text = "\n---\n".join(top_contexts)
    
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
    
    # 連續問答迴圈
    print("\n" + "=" * 50)
    print("PDF 處理完成！現在可以開始問問題了。")
    print("輸入 'q' 或 'exit' 離開程式")
    print("=" * 50)
    
    while True:
        try:
            query = input("\n您想查詢什麼：").strip()
            
            if not query:
                continue
            
            if query.lower() in ['q', 'exit', 'quit', '離開']:
                print("\n程式已結束")
                break
            
            print("\n" + "-" * 50)
            search_and_answer(query)
            print("-" * 50)
            
        except EOFError:
            print("\n程式已結束")
            break
        except KeyboardInterrupt:
            print("\n\n程式已中斷")
            break
        except Exception as e:
            print(f"\n發生錯誤: {e}")
            continue
