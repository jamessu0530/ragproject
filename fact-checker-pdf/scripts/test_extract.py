#!/usr/bin/env python3
"""
測試 PDF 提取結果
顯示 extract_text_from_pdf 的詳細輸出
"""
import sys
import os
import json

# 加入父目錄到 path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.pdf_utils.extract import extract_text_from_pdf

def test_extract(pdf_path: str):
    """測試單一 PDF 的提取結果"""
    print("=" * 80)
    print(f"測試檔案: {pdf_path}")
    print("=" * 80)
    
    text_blocks = extract_text_from_pdf(pdf_path)
    
    if not text_blocks:
        print("❌ 沒有提取到任何文字")
        return
    
    print(f"\n✅ 共提取到 {len(text_blocks)} 個 text blocks\n")
    
    # 顯示所有 blocks 的詳細資訊
    for i, block in enumerate(text_blocks, 1):
        print(f"--- Block {i} ---")
        print(f"Page: {block.get('page')}")
        print(f"Type: {block.get('type')}")
        print(f"Text 長度: {len(block.get('text', ''))} 字元")
        print(f"Text 內容: {block.get('text', '')}")
        print()
    
    # 統計資訊
    print("\n" + "=" * 80)
    print("統計資訊")
    print("=" * 80)
    
    # Type 統計
    type_counts = {}
    for block in text_blocks:
        block_type = block.get('type', 'Unknown')
        type_counts[block_type] = type_counts.get(block_type, 0) + 1
    
    print(f"\nType 分布:")
    for type_name, count in sorted(type_counts.items(), key=lambda x: -x[1]):
        print(f"  {type_name}: {count}")
    
    # Page 統計
    pages = sorted({b.get('page') for b in text_blocks if b.get('page') is not None})
    print(f"\n頁碼範圍: {pages[0]} - {pages[-1]}" if pages else "\n無頁碼資訊")
    
    # 文字長度統計
    text_lengths = [len(b.get('text', '')) for b in text_blocks]
    print(f"\n文字長度:")
    print(f"  最小: {min(text_lengths)}")
    print(f"  最大: {max(text_lengths)}")
    print(f"  平均: {sum(text_lengths) // len(text_lengths)}")

if __name__ == "__main__":
    # 測試 pdfs 資料夾中的第一個 PDF
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    pdfs_folder = os.path.join(project_root, "pdfs")
    
    pdf_files = [f for f in os.listdir(pdfs_folder) if f.lower().endswith('.pdf')]
    
    if not pdf_files:
        print("❌ pdfs 資料夾中沒有 PDF 檔案")
    else:
        # 測試第一個 PDF
        pdf_path = os.path.join(pdfs_folder, pdf_files[0])
        test_extract(pdf_path)
