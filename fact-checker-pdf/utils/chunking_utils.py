

def chunk_blocks(text_blocks: list[dict], chunk_size: int = 900) -> list[dict]:
    """
    以 block 為單位進行 chunking，保留 page 資訊
    
    不進行二次 split，chunk 邊界嚴格對應 block 邊界，確保 pages 準確
    
    Args:
        text_blocks: 文字塊清單，每個 dict 包含 "page", "text", "type"
        chunk_size: chunk 大小（字元數）
    
    Returns:
        chunk 清單，每個 dict 包含 "text", "pages", "types"
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
                types = sorted({b.get("type") for b in current_blocks if b.get("type") is not None})
                
                chunks.append({
                    "text": current_text.strip(),
                    "pages": pages if pages else None,
                    "types": types if types else None
                })
            
            # 超大 block 自己單獨成 chunk
            chunks.append({
                "text": block_text,
                "pages": [block.get("page")] if block.get("page") is not None else None,
                "types": [block.get("type")] if block.get("type") is not None else None
            })
            
            # 清空累積
            current_text = ""
            current_blocks = []
            continue
        
        # 嘗試將新 block 加入當前文字（用空格分隔）
        test_text = current_text + " " + block_text if current_text else block_text
        
        # 如果加入後超過 chunk_size，輸出當前 chunk 並清空
        if len(test_text) > chunk_size and current_text:
            pages = sorted({b.get("page") for b in current_blocks if b.get("page") is not None})
            types = sorted({b.get("type") for b in current_blocks if b.get("type") is not None})
            
            chunks.append({
                "text": current_text.strip(),
                "pages": pages if pages else None,
                "types": types if types else None
            })
            
            # 清空，準備新的 chunk（只加入新 block，不要用 test_text）
            current_text = block_text
            current_blocks = [block]
        else:
            # 可以安全加入，使用 test_text
            current_text = test_text
            current_blocks.append(block)
    
    # 處理最後剩餘的
    if current_text.strip():
        pages = sorted({b.get("page") for b in current_blocks if b.get("page") is not None})
        types = sorted({b.get("type") for b in current_blocks if b.get("type") is not None})
        
        chunks.append({
            "text": current_text.strip(),
            "pages": pages if pages else None,
            "types": types if types else None
        })
    
    print(f"已切分為 {len(chunks)} 個片段（以 block 為單位）")
    return chunks
