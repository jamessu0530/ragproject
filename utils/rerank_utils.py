import os
import cohere
from dotenv import load_dotenv

load_dotenv()
co = cohere.ClientV2(api_key=os.getenv("COHERE_API_KEY"))
def rerank_documents(query: str, documents: list[str], top_n: int = 3):
    if not documents:
        return []
        
    try:
        response = co.rerank(
            model="rerank-v3.5",  
            query=query,
            documents=documents,
            top_n=top_n,
        )
        ranked_docs = []
        for result in response.results:
            # V2 API 回傳的是 index要回頭去 documents 列表拿文字，以前直接回傳文字
            doc_text = documents[result.index]
            ranked_docs.append((result.relevance_score, doc_text))
            
        return ranked_docs
        
    except Exception as e:
        print(f"Cohere Rerank failed: {e}")
        # 如果失敗，回傳原順序 (當作 score=0)
        return [(0.0, doc) for doc in documents[:top_n]]
