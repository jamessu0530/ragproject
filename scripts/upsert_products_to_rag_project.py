#!/usr/bin/env python3
# upsert_products_to_rag_project.py
# 將商品資料 upsert 到 rag_project 向量資料庫
import sys
import os

# 將專案根目錄加入 sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tqdm import tqdm
from deep_translator import GoogleTranslator
from dotenv import load_dotenv
from pinecone import Pinecone
from utils.embedding_utils import get_embedding
from NTOUutils.ntou_api import get_all_product_ids, get_product_details

load_dotenv()

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

def get_rag_project_index():
    """取得 rag-project index"""
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    return pc.Index("rag-project")

def embed_and_upsert_products_to_rag_project():
    """
    取得所有產品資料 -> 翻譯並合併中英文 -> 轉向量 -> 寫入 rag_project
    """
    try:
        index = get_rag_project_index()
        namespace = "ntou-products"
        print(f"已連接 Pinecone Index: rag-project")
        print(f"目標 Namespace: {namespace}")
    except Exception as e:
        print(f"Pinecone 連接失敗: {e}")
        return

    print("正在取得所有產品 ID...")
    all_ids = get_all_product_ids()
    
    if not all_ids:
        print("未找到任何產品 ID，程式結束。")
        return

    total_products = len(all_ids)
    print(f"共找到 {total_products} 個產品。開始進行 Embedding 與 Upsert (包含自動翻譯)...")

    vectors = []
    batch_size = 50
    
    for product_id in tqdm(all_ids, desc="處理進度"):
        details = get_product_details(product_id)
        if not details:
            continue
            
        # 避免 None
        name = details.get("productName") or ""
        description = details.get("productDescription") or ""
        
        # 翻譯成英文
        name_en = translate_to_english(name)
        desc_en = translate_to_english(description)
        
        # 組合中英文內容
        # 格式：
        # 產品名稱: {中文}
        # Product Name: {英文}
        # 產品描述: {中文}
        # Product Description: {英文}
        
        text_content = (
            f"產品名稱: {name}\n"
            f"Product Name: {name_en}\n"
            f"產品描述: {description}\n"
            f"Product Description: {desc_en}"
        )
        
        embedding = get_embedding(text_content, task_type="retrieval_document")
        
        if not embedding:
            # 失敗也沒關係，跳過
            continue
            
        vector = {
            "id": product_id,
            "values": embedding,
            "metadata": {
                "productName": name,
                "productDescription": description,
                "text": text_content,  # 包含雙語的完整文本
                "type": "product"
            }
        }
        vectors.append(vector)
        
        if len(vectors) >= batch_size:
            try:
                index.upsert(vectors=vectors, namespace=namespace)
                vectors = []
            except Exception as e:
                print(f"批次寫入失敗: {e}")

    if vectors:
        try:
            index.upsert(vectors=vectors, namespace=namespace)
        except Exception as e:
            print(f"最後批次寫入失敗: {e}")

    print(f"\n✅ 完成！已將 {total_products} 筆產品資料寫入 rag-project (Namespace: {namespace})")

if __name__ == "__main__":
    print("=" * 60)
    print("將商品資料 Upsert 到 rag-project 向量資料庫")
    print("=" * 60)
    embed_and_upsert_products_to_rag_project()

