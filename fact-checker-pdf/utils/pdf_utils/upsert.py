import sys
import os
import time
import hashlib
from deep_translator import GoogleTranslator
from utils.pinecone_utils import get_pinecone_index
from utils.embedding_utils import get_embedding
from utils.chunking_utils import split_text_into_chunks
from utils.pdf_utils.extract import extract_text_from_pdf

def translate_to_english(text: str) -> str:
    """
    將中文文字翻譯成英文
    """
    try:
        if not text or len(text.strip()) == 0:
            return ""
        translator = GoogleTranslator(source='zh-TW', target='en')
        translation = translator.translate(text)
        return translation
    except Exception as e:
        print(f"翻譯失敗: {e}")
        return text  # 翻譯失敗時回傳原文

index = get_pinecone_index()

def get_file_hash(file_path: str) -> str:
    """生成檔案路徑的 hash 值作為唯一識別碼"""
    return hashlib.md5(file_path.encode()).hexdigest()

def fetch_and_process_pdf(pdf_path: str, namespace: str):
    """
    1. 讀取 PDF 檔案
    2. 切片 (Chunking)
    3. 存入 Pinecone (Upsert)
    """
    # 1. 讀取 PDF
    text = extract_text_from_pdf(pdf_path)
    if not text:
        return False
    
    # 2. 切片
    chunks = split_text_into_chunks(text)
    if not chunks:
        print("內容太短跳過儲存")
        return False
    
    # 3. 存入 Pinecone（先翻譯成英文再 embedding，但保留中文原文在 metadata）
    file_hash = get_file_hash(pdf_path)
    vectors = []
    for idx, chunk in enumerate(chunks):
        unique_id = f"{file_hash}_{idx}"
        
        # 翻譯成英文（用於 embedding）
        print(f"正在翻譯片段 {idx+1}/{len(chunks)}...")
        chunk_en = translate_to_english(chunk)
        
        # 用英文做 embedding（提高搜尋準確度）
        embedding = get_embedding(chunk_en)
        
        # 如果 embedding 失敗（回傳 None），跳過這個 chunk
        if embedding is None:
            print(f"⚠️  片段 {idx} embedding 失敗，跳過")
            continue
        
        vector = {
            "id": unique_id,
            "values": embedding,  # 用英文 embedding
            "metadata": {
                "text": chunk,  # 保留中文原文（給 Gemma 回答時用）
                "text_en": chunk_en,  # 也保留英文版本（可選）
                "file_path": pdf_path,
                "file_name": os.path.basename(pdf_path),
                "chunk_index": idx
            }
        }
        vectors.append(vector)
    
    # 如果沒有任何有效的向量，回傳 False
    if not vectors:
        print("❌ 所有片段 embedding 都失敗，無法寫入資料")
        return False
    
    # 批次寫入
    batch_size = 100
    for i in range(0, len(vectors), batch_size):
        batch = vectors[i:i+batch_size]
        try:
            index.upsert(vectors=batch, namespace=namespace)
        except Exception as e:
            print(f"❌ 批次寫入失敗: {e}")
            return False
    
    print(f"寫入 {len(vectors)} 筆資料到 namespace='{namespace}' (ID prefix: {file_hash})")
    
    # 等待索引生效
    print("睡十秒")
    time.sleep(10)
    return True

def fetch_and_process_pdf_folder(folder_path: str, namespace: str):
    """
    讀取資料夾內所有 PDF 檔案並處理
    
    Args:
        folder_path: 資料夾路徑
        namespace: Pinecone namespace
        
    Returns:
        成功處理的檔案數量
    """
    if not os.path.isdir(folder_path):
        print(f"資料夾不存在：{folder_path}")
        return 0
    
    # 找出所有 PDF 檔案
    pdf_files = []
    for file in os.listdir(folder_path):
        if file.lower().endswith('.pdf'):
            pdf_files.append(os.path.join(folder_path, file))
    
    if not pdf_files:
        print(f"資料夾中沒有找到 PDF 檔案：{folder_path}")
        return 0
    
    print(f"\n找到 {len(pdf_files)} 個 PDF 檔案，開始處理...")
    print("=" * 50)
    
    success_count = 0
    for idx, pdf_path in enumerate(pdf_files, 1):
        print(f"\n[{idx}/{len(pdf_files)}] 處理：{os.path.basename(pdf_path)}")
        print("-" * 50)
        if fetch_and_process_pdf(pdf_path, namespace):
            success_count += 1
        else:
            print(f"處理失敗：{os.path.basename(pdf_path)}")
    
    print("\n" + "=" * 50)
    print(f"處理完成！成功：{success_count}/{len(pdf_files)}")
    return success_count
