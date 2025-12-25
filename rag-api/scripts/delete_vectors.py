# delete_vectors.py
# 刪除 Pinecone 向量資料庫中指定 namespace 的所有資料
import os
from dotenv import load_dotenv
from utils.pinecone_utils import get_pinecone_index

load_dotenv()

def delete_all_vectors(namespace="ntou-products"):
    """
    刪除指定 namespace 中的所有向量資料
    """
    try:
        index = get_pinecone_index()
        print(f"已連接 Pinecone Index: {os.getenv('PINECONE_INDEX')}")
        print(f"準備刪除 Namespace: '{namespace}' 中的所有資料...")
        
        # 確認操作
        response = input(f"確定要刪除 namespace '{namespace}' 中的所有資料嗎？(yes/no): ")
        if response.lower() != 'yes':
            print("操作已取消。")
            return
        
        # 刪除所有資料
        print("正在刪除所有向量資料...")
        index.delete_all(delete_all=True, namespace=namespace)
        
        print(f"✅ 成功刪除 namespace '{namespace}' 中的所有資料！")
        print("現在可以重新執行資料抓取腳本了。")
        
    except Exception as e:
        print(f"❌ 刪除過程中發生錯誤: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # 預設刪除 ntou-products namespace
    # 如果需要刪除其他 namespace，可以修改這裡
    delete_all_vectors(namespace="ntou-products")
