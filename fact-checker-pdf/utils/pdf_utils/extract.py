import os
from pypdf import PdfReader

def extract_text_from_pdf(pdf_path: str) -> str | None:
    """
    從 PDF 檔案中提取文字內容
    
    Args:
        pdf_path: PDF 檔案的路徑
        
    Returns:
        提取的文字內容，如果失敗則返回 None
    """
    if not os.path.exists(pdf_path):
        print(f"檔案不存在：{pdf_path}")
        return None
    
    if not pdf_path.lower().endswith('.pdf'):
        print(f"檔案不是 PDF 格式：{pdf_path}")
        return None
    
    try:
        print(f"正在讀取 PDF：{pdf_path}")
        reader = PdfReader(pdf_path)
        
        # 提取所有頁面的文字
        text_parts = []
        total_pages = len(reader.pages)
        print(f"PDF 共有 {total_pages} 頁")
        
        for page_num, page in enumerate(reader.pages, 1):
            try:
                text = page.extract_text()
                if text.strip():
                    text_parts.append(text)
                    print(f"已讀取第 {page_num}/{total_pages} 頁")
            except Exception as e:
                print(f"讀取第 {page_num} 頁時發生錯誤：{e}")
                continue
        
        if not text_parts:
            print("PDF 中沒有找到文字內容")
            return None
        
        # 合併所有文字，用換行分隔
        full_text = "\n\n".join(text_parts)
        
        # 清理文字：移除多餘的空白
        cleaned_lines = [line.strip() for line in full_text.split('\n') if line.strip()]
        result = "\n".join(cleaned_lines)
        
        print(f"成功提取 {len(result)} 個字元")
        return result
        
    except Exception as e:
        print(f"讀取 PDF 失敗：{e}")
        return None
