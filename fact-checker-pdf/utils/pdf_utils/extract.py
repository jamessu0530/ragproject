from unstructured.partition.pdf import partition_pdf

def extract_text_from_pdf(pdf_path: str) -> list[dict] | None:
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
            
            # 安全取用 bbox 資訊
            bbox = None
            try:
                if hasattr(element, 'metadata') and element.metadata:
                    coordinates = getattr(element.metadata, 'coordinates', None)
                    if coordinates:
                        if hasattr(coordinates, 'points'):
                            # 轉換為 [x1, y1, x2, y2] 格式
                            points = coordinates.points
                            if points and len(points) >= 4:
                                x_coords = [p[0] for p in points if isinstance(p, (list, tuple)) and len(p) >= 2]
                                y_coords = [p[1] for p in points if isinstance(p, (list, tuple)) and len(p) >= 2]
                                if x_coords and y_coords:
                                    bbox = [min(x_coords), min(y_coords), max(x_coords), max(y_coords)]
                        elif isinstance(coordinates, (list, tuple)) and len(coordinates) >= 4:
                            # 已經是 [x1, y1, x2, y2] 格式
                            bbox = list(coordinates[:4])
                
                if bbox is None and hasattr(element, 'bbox'):
                    bbox_val = element.bbox
                    if isinstance(bbox_val, (list, tuple)) and len(bbox_val) >= 4:
                        bbox = list(bbox_val[:4])
            except Exception:
                bbox = None
            
            text_blocks.append({
                "page": page,
                "text": text,
                "bbox": bbox
            })
    
    if not text_blocks:
        return None
    
    return text_blocks
