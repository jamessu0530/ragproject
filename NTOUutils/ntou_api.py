import requests
import os
from dotenv import load_dotenv

load_dotenv()

# 從環境變數讀取後端 API URL，預設為 localhost:8080
PRODUCT_API_BASE_URL = os.getenv("PRODUCT_API_BASE_URL", "http://localhost:8080")

def get_all_product_ids():
    """
    取得所有產品的 ID。
    透過分頁機制 (page loop) 獲取完整列表。
    API: GET {PRODUCT_API_BASE_URL}/api/products
    """
    base_url = f"{PRODUCT_API_BASE_URL}/api/products"
    all_ids = []
    page = 1
    page_size = 20  # 每次取 20 筆，可依需求調整
    
    print("開始取得所有產品列表...")
    
    while True:
        try:
            params = {
                "page": page,
                "pageSize": page_size
            }
            response = requests.get(base_url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if not data:
                break
                
            for item in data:
                if "productID" in item:
                    all_ids.append(item["productID"])
            
            print(f"已讀取第 {page} 頁，目前共收集 {len(all_ids)} 筆 ID")
            
            if len(data) < page_size:
                break
                
            page += 1
            
        except requests.exceptions.RequestException as e:
            print(f"取得列表時發生錯誤 (Page {page}): {e}")
            break
            
    return all_ids

def get_product_details(product_id):
    """
    根據 Product ID 取得產品資訊，並只回傳 productName 與 productDescription。
    """
    base_url = f"{PRODUCT_API_BASE_URL}/api/products"
    url = f"{base_url}/{product_id}"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        product_name = data.get("productName")
        product_description = data.get("productDescription")

        return {
            "productName": product_name,
            "productDescription": product_description
        }

    except requests.exceptions.RequestException as e:
        print(f"取得產品詳情錯誤 (ID: {product_id}): {e}")
        return None
    except Exception as e:
        print(f"發生未預期的錯誤 (ID: {product_id}): {e}")
        return None

