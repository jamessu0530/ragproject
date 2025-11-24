from langchain_text_splitters import RecursiveCharacterTextSplitter

def split_text_into_chunks(text: str, chunk_size: int = 900, chunk_overlap: int = 200) -> list[str]:
    """
    使用 Token-based 策略將長文字切片
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

