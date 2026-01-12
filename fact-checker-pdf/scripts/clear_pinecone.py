#!/usr/bin/env python3
"""
清除 Pinecone 中的所有向量資料
"""
import sys
import os

# 加入父目錄到 path，讓 Python 能找到 utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dotenv import load_dotenv
from utils.pinecone_utils import get_pinecone_index

load_dotenv()
index = get_pinecone_index()

# 要清除的 namespace
NAMESPACE = "web-check"

def clear_namespace():
    """清除指定 namespace 的所有向量"""
    try:
        print(f"正在清除 namespace: {NAMESPACE}")
        
        # 刪除整個 namespace 的所有向量
        index.delete(delete_all=True, namespace=NAMESPACE)
        
        print(f"✅ 成功清除 namespace '{NAMESPACE}' 的所有資料")
        
        # 驗證是否清空
        stats = index.describe_index_stats()
        namespace_count = stats.get('namespaces', {}).get(NAMESPACE, {}).get('vector_count', 0)
        
        if namespace_count == 0:
            print(f"✅ 驗證成功：namespace '{NAMESPACE}' 現在是空的")
        else:
            print(f"⚠️  警告：namespace '{NAMESPACE}' 仍有 {namespace_count} 筆資料")
            
    except Exception as e:
        print(f"❌ 清除失敗: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("=" * 60)
    print("Pinecone 資料清除工具")
    print("=" * 60)
    print(f"Index: {os.getenv('PINECONE_INDEX')}")
    print(f"Namespace: {NAMESPACE}")
    print("=" * 60)
    
    # 確認操作
    confirm = input("\n⚠️  確定要清除所有資料嗎？(輸入 'yes' 確認): ")
    
    if confirm.lower() == 'yes':
        clear_namespace()
    else:
        print("\n❌ 操作已取消")
