import sys
import os

# 將專案根目錄加入 sys.path 以便匯入 utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import ollama
from dotenv import load_dotenv
from utils.pinecone_utils import get_pinecone_index
from utils.embedding_utils import get_embedding
from utils.rerank_utils import rerank_documents

# 載入環境變數
load_dotenv()

# 初始化 Pinecone
index = get_pinecone_index()

def get_best_context(query_text: str, retrieve_k: int = 15, top_k: int = 3):
    """
    RAG 流程：Retrieve -> Rerank (Cohere) -> Return Top K
    """
    print(f"🔍 1. [Retrieve] 正在資料庫搜尋 Top {retrieve_k} 筆資料...")
    
    # --- 步驟 1: Retrieve (粗篩) ---
    query_vector = get_embedding(query_text)
    results = index.query(
        vector=query_vector,
        top_k=retrieve_k,
        include_metadata=True,
        namespace="default"
    )
    
    # 整理 Retrieve 結果
    candidates = []
    for match in results["matches"]:
        text = match["metadata"].get("text", "")
        candidates.append(text)
    
    if not candidates:
        return "沒有找到相關資料。"

    print(f"⚖️  2. [Rerank] 正在使用 Cohere 重排 {len(candidates)} 筆資料...")

    # --- 步驟 2: Rerank (Cohere) ---
    # 呼叫 rerank_utils
    ranked_results = rerank_documents(query_text, candidates, top_n=top_k)
    
    # --- 步驟 3: 顯示結果 ---
    final_contexts = []
    print(f"✅ 3. [Result] 最終選出的 Top {top_k}：")
    for score, text in ranked_results:
        # Cohere score is usually 0-1
        print(f"   - (Rerank分數: {score:.4f}) {text[:50]}...")
        final_contexts.append(text)
    
    return "\n\n".join(final_contexts)

def generate_answer(query: str, context: str):
    """
    步驟 4: Generate (呼叫本地 Ollama 生成回答)
    """
    print("🤖 4. [Generate] 正在呼叫本地 Ollama (gemma3:4b) 生成回答...")
    
    prompt = f"""你是一個專業的知識庫助理。請根據以下的【參考資料】來回答使用者的問題。
請用繁體中文回答，並保持語氣親切。

【參考資料】：
{context}

【使用者問題】：
{query}

【回答】：
"""
    
    response = ollama.chat(model='gemma3:4b', messages=[
        {
            'role': 'user',
            'content': prompt,
        },
    ])
    
    return response['message']['content']

if __name__ == "__main__":
    # 請在這裡輸入你想查詢的問題
    user_query = "請根據資料庫內容回答我的問題"
    print(f"🗣️  使用者問題：{user_query}")
    print("-" * 50)
    
    # 1. 取得上下文
    best_context = get_best_context(user_query)
    
    # 2. 生成回答
    if best_context and best_context != "沒有找到相關資料。":
        answer = generate_answer(user_query, best_context)
        print("-" * 50)
        print("📝 最終回答：")
        print(answer)
    else:
        print("❌ 找不到足夠資料來回答。")
