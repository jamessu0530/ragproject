import sys
import os

# 將專案根目錄加入 sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from NTOUutils.ntou_embedding import embed_and_upsert_products
from NTOUutils.ntou_search import search_products

if __name__ == "__main__":
    embed_and_upsert_products()
    user_input = input("\n[搜尋] 請輸入您的問題: ").strip()
    if user_input:
        results = search_products(user_input)
        
        # 因為 search_products 現在回傳 list，CLI 顯示需要自己 print
        print(f"\n搜尋結果 (共 {len(results)} 筆):")
        print("-" * 50)
        
        if not results:
            print("找不到符合條件的產品。")
        else:
            for item in results:
                print(f"Rank {item['rank']} | Score: {item['score']:.4f} | ID: {item['id']}")
                print(f"產品名稱: {item['productName']}")
                desc = item['productDescription']
                display_desc = (desc[:50] + '...') if len(desc) > 50 else desc
                print(f"產品描述: {display_desc}")
                print("-" * 50)
