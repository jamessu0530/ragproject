from deep_translator import GoogleTranslator
from utils.embedding_utils import get_embedding
from utils.pinecone_utils import get_pinecone_index

def translate_to_english(text):
    if not text or len(text.strip()) == 0:
        return ""
    
    translator = GoogleTranslator(source='zh-TW', target='en')
    translation = translator.translate(text)
    return translation
def search_products(query_text):
    index = get_pinecone_index()
    namespace = "ntou-products"
    english_query = translate_to_english(query_text)
    combined_query = f"{query_text} {english_query}"
    query_vector = get_embedding(combined_query, task_type="retrieval_query")
    if not query_vector:
        print("Embedding 失敗，無法進行搜尋。")
        return []
    results = index.query(vector=query_vector, top_k=10, include_metadata=True, namespace=namespace)
    matches = results.get('matches', [])
    filtered_matches = [m for m in matches if m['score'] >= 0.3]
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

    return []
