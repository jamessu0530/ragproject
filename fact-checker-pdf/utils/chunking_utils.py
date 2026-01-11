from langchain_text_splitters import RecursiveCharacterTextSplitter

def split_text_into_chunks(text: str, chunk_size: int = 900, chunk_overlap: int = 200) -> list[str]:
    """
    使用字元數（character）策略將長文字切片
    """
    if not text:
        return []

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", "。", "！", "？", " ", ""]
    )
    
    chunks = text_splitter.split_text(text)
    print(f"已切分為 {len(chunks)} 個片段")
    
    return chunks

def chunk_blocks(text_blocks: list[dict], chunk_size: int = 900, chunk_overlap: int = 200) -> list[dict]:
    """
    以 block 為單位進行 chunking，保留 page/bbox 資訊
    
    不進行二次 split，chunk 邊界嚴格對應 block 邊界，確保 pages/bboxes 準確
    
    Args:
        text_blocks: 文字塊清單，每個 dict 包含 "page", "text", "bbox"
        chunk_size: chunk 大小（字元數）
        chunk_overlap: chunk 重疊大小（字元數）
    
    Returns:
        chunk 清單，每個 dict 包含 "text", "pages", "bboxes"
    """
    if not text_blocks:
        return []
    
    chunks = []
    current_text = ""
    current_blocks = []  # 追蹤當前累積的 blocks
    
    for block in text_blocks:
        block_text = block.get("text", "").strip()
        if not block_text:
            continue
        
        # 處理單一 block 超過 chunk_size 的情況
        if len(block_text) > chunk_size:
            # 先 flush 當前累積的內容
            if current_text.strip():
                pages = sorted({b.get("page") for b in current_blocks if b.get("page") is not None})
                bboxes = [b.get("bbox") for b in current_blocks if b.get("bbox") is not None]
                
                chunks.append({
                    "text": current_text.strip(),
                    "pages": pages if pages else None,
                    "bboxes": bboxes if bboxes else None
                })
            
            # 超大 block 自己單獨成 chunk
            chunks.append({
                "text": block_text,
                "pages": [block.get("page")] if block.get("page") is not None else None,
                "bboxes": [block.get("bbox")] if block.get("bbox") is not None else None
            })
            
            # 清空累積
            current_text = ""
            current_blocks = []
            continue
        
        # 嘗試將新 block 加入當前文字
        test_text = current_text + "\n\n" + block_text if current_text else block_text
        
        # 如果加入後超過 chunk_size，輸出當前 chunk（不 split）
        if len(test_text) > chunk_size and current_text:
            # 輸出當前 chunk，pages/bboxes 準確對應 current_blocks
            pages = sorted({b.get("page") for b in current_blocks if b.get("page") is not None})
            bboxes = [b.get("bbox") for b in current_blocks if b.get("bbox") is not None]
            
            chunks.append({
                "text": current_text.strip(),
                "pages": pages if pages else None,
                "bboxes": bboxes if bboxes else None
            })
            
            # 處理 overlap：保留最後 N 個 blocks 直到達到 overlap 大小
            if chunk_overlap <= 0:
                # overlap 為 0 或負數時，直接清空
                current_text = ""
                current_blocks = []
            else:
                overlap_text = ""
                overlap_blocks = []
                
                # 從後往前累加 blocks，直到達到 overlap 大小
                for b in reversed(current_blocks):
                    b_text = b.get("text", "").strip()
                    if not b_text:
                        continue
                    
                    test_overlap = b_text + "\n\n" + overlap_text if overlap_text else b_text
                    
                    if len(test_overlap) >= chunk_overlap:
                        overlap_text = test_overlap
                        overlap_blocks.insert(0, b)
                        break
                    else:
                        overlap_text = test_overlap
                        overlap_blocks.insert(0, b)
                
                # 如果沒有達到 overlap，至少保留最後一個 block
                if not overlap_blocks:
                    overlap_text = current_blocks[-1].get("text", "").strip()
                    overlap_blocks = [current_blocks[-1]]
                
                current_text = overlap_text
                current_blocks = overlap_blocks
        
        # 加入新 block
        current_text = test_text
        current_blocks.append(block)
    
    # 處理最後剩餘的
    if current_text.strip():
        pages = sorted({b.get("page") for b in current_blocks if b.get("page") is not None})
        bboxes = [b.get("bbox") for b in current_blocks if b.get("bbox") is not None]
        
        chunks.append({
            "text": current_text.strip(),
            "pages": pages if pages else None,
            "bboxes": bboxes if bboxes else None
        })
    
    print(f"已切分為 {len(chunks)} 個片段（以 block 為單位）")
    return chunks
