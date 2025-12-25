from deep_translator import GoogleTranslator
from utils.embedding_utils import get_embedding
from utils.pinecone_utils import get_pinecone_index

def translate_to_english(text):
    """
    使用 deep-translator 將輸入文字翻譯成英文
    """
    try:
        if not text or len(text.strip()) == 0:
            return ""
        translator = GoogleTranslator(source='zh-TW', target='en')
        translation = translator.translate(text)
        return translation
    except Exception as e:
        print(f"翻譯失敗: {e}")
        return ""

def search_products(query_text):
    """
    搜尋 Pinecone 中的產品資料
    回傳 List[Dict] 格式，方便 API 使用
    """
    try:
        index = get_pinecone_index()
        namespace = "ntou-products"

        # 翻譯查詢
        english_query = translate_to_english(query_text)
        
        if english_query:
            combined_query = f"{query_text} {english_query}"
        else:
            combined_query = query_text
            
        print(f"正在將合併查詢轉為向量: '{combined_query}'...")
        query_vector = get_embedding(combined_query, task_type="retrieval_query")

        if not query_vector:
            print("Embedding 失敗，無法進行搜尋。")
            return []

        print(f"正在 Pinecone (namespace='{namespace}') 進行搜尋...")
        results = index.query(
            vector=query_vector,
            top_k=10,
            include_metadata=True,
            namespace=namespace
        )

        matches = results.get('matches', [])
        
        # 過濾分數低於 0.5
        filtered_matches = [m for m in matches if m['score'] >= 0.5]
        
        output_list = []
        for i, match in enumerate(filtered_matches, 1):
            score = match['score']
            product_id = match['id']
            metadata = match.get('metadata', {})
            
            output_list.append({
                "rank": i,
                "score": score,
                "id": product_id,
                "productName": metadata.get('productName', 'N/A'),
                "productDescription": metadata.get('productDescription', 'N/A')
            })
            
        return output_list

    except Exception as e:
        print(f"搜尋過程中發生錯誤: {e}")
        return []
