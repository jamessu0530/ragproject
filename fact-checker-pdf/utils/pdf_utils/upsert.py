import os
import hashlib
from utils.pinecone_utils import get_pinecone_index
from utils.embedding_utils import get_embedding
from utils.chunking_utils import chunk_blocks
from utils.pdf_utils.extract import extract_text_from_pdf

index = get_pinecone_index()

def get_file_hash(file_path: str) -> str:
    return hashlib.md5(file_path.encode()).hexdigest()

def fetch_and_process_pdf(pdf_path: str, namespace: str):
    text_blocks = extract_text_from_pdf(pdf_path)
    if not text_blocks:
        return False
    
    # 以 block 為單位進行 chunking，保留 page/bbox 資訊
    chunks = chunk_blocks(text_blocks)
    
    file_hash = get_file_hash(pdf_path)
    vectors = []
    for idx, chunk in enumerate(chunks):
        unique_id = f"{file_hash}_{idx}"
        embedding = get_embedding(chunk["text"])
        
        if embedding is None:
            continue
        
        # chunk 天生知道自己來自哪些 page/bbox
        vector = {
            "id": unique_id,
            "values": embedding,
            "metadata": {
                "text": chunk["text"],
                "file_path": pdf_path,
                "file_name": os.path.basename(pdf_path),
                "chunk_index": idx,
                "pages": chunk.get("pages"),
                "bboxes": chunk.get("bboxes")
            }
        }
        vectors.append(vector)
    
    batch_size = 100
    for i in range(0, len(vectors), batch_size):
        batch = vectors[i:i+batch_size]
        index.upsert(vectors=batch, namespace=namespace)
    
    return True

def fetch_and_process_pdf_folder(folder_path: str, namespace: str):
    pdf_files = []
    for file in os.listdir(folder_path):
        if file.lower().endswith('.pdf'):
            pdf_files.append(os.path.join(folder_path, file))
    
    success_count = 0
    for pdf_path in pdf_files:
        if fetch_and_process_pdf(pdf_path, namespace):
            success_count += 1
    
    return success_count
