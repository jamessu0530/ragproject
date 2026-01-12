import re
import warnings
from unstructured.partition.pdf import partition_pdf

# 隱藏 unstructured 的警告訊息
warnings.filterwarnings("ignore", category=UserWarning, module="unstructured")
warnings.filterwarnings("ignore", message=".*No features in text.*")
warnings.filterwarnings("ignore", message=".*No languages specified.*")

def clean_text(text: str) -> str:
    bopomofo_pattern = r'[\u3105-\u312F\u02C7\u02CA\u02CB\u02D9]'
    text = re.sub(bopomofo_pattern, '', text)
    text = text.replace('\n', ' ')
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    return text
def extract_text_from_pdf(pdf_path: str) -> list[dict] | None:
    # 不指定語言，讓 unstructured 自動偵測（支援所有語言）
    elements = partition_pdf(pdf_path)
    
    has_text = any(hasattr(e, "text") and e.text.strip() for e in elements)
    
    if not has_text:
        print("這是掃描 PDF，要走 OCR")
        elements = partition_pdf(pdf_path, strategy="ocr_only")
    
    text_blocks = []
    for element in elements:
        if hasattr(element, 'text') and element.text:
            text = element.text.strip()
            if not text:
                continue
            
            # 安全取用 page 資訊
            page = None
            if hasattr(element, 'metadata') and element.metadata:
                page = getattr(element.metadata, 'page_number', None)
            if page is None and hasattr(element, 'page_number'):
                page = element.page_number
            
            
            # 清理文字：移除注音符號、換行符號和多餘空白
            text = clean_text(text)
            
            # 過濾太短的文字（< 10 字元）
            if len(text) < 10:
                continue
            
            # 過濾頁碼：如果是純數字且很短（< 5 字元），可能是頁碼，跳過
            if text.isdigit() and len(text) <= 4:
                continue
            
            # 移除注音後可能變成空字串
            if not text:
                continue
            
            text_blocks.append({
                "page": page,
                "text": text,
                "type": getattr(element, "category", element.__class__.__name__)
            })
    
    if not text_blocks:
        return None
    
    return text_blocks
