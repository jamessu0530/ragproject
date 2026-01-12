


def chunk_blocks(text_blocks: list[dict], chunk_size: int = 500, max_page_span: int = 2) -> list[dict]:
    """
    語意結構導向的 chunking
    
    策略：
    1. Title = 強制邊界
    2. 同一 chunk 最多跨 max_page_span 頁
    3. 不切斷 block
    4. chunk_size 為上限
    """
    if not text_blocks:
        return []
    
    chunks = []
    current_text = ""
    current_blocks = []
    
    def flush_chunk():
        if not current_text.strip():
            return
        
        pages = sorted({b.get("page") for b in current_blocks if b.get("page") is not None})
        seen = set()
        types = []
        for b in current_blocks:
            t = b.get("type")
            if t and t not in seen:
                types.append(t)
                seen.add(t)
        
        chunks.append({
            "text": current_text.strip(),
            "pages": pages if pages else None,
            "types": types if types else None
        })
    
    for block in text_blocks:
        block_text = block.get("text", "").strip()
        block_type = block.get("type", "")
        block_page = block.get("page")
        
        if not block_text:
            continue
        
        # Title = 強制邊界
        if block_type == "Title" and current_text:
            flush_chunk()
            current_text = ""
            current_blocks = []
        
        # 檢查頁數跨度
        if current_blocks and block_page is not None:
            current_pages = {b.get("page") for b in current_blocks if b.get("page") is not None}
            if current_pages:
                page_span = max(current_pages | {block_page}) - min(current_pages | {block_page}) + 1
                if page_span > max_page_span:
                    flush_chunk()
                    current_text = ""
                    current_blocks = []
        
        # 超大 block 單獨處理
        if len(block_text) > chunk_size:
            flush_chunk()
            chunks.append({
                "text": block_text,
                "pages": [block_page] if block_page is not None else None,
                "types": [block_type] if block_type else None
            })
            current_text = ""
            current_blocks = []
            continue
        
        test_text = current_text + "\n\n" + block_text if current_text else block_text
        
        if len(test_text) > chunk_size and current_text:
            flush_chunk()
            current_text = block_text
            current_blocks = [block]
        else:
            current_text = test_text
            current_blocks.append(block)
    
    flush_chunk()
    
    print(f"已切分為 {len(chunks)} 個片段")
    return chunks
