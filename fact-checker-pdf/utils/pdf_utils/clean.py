import re
from collections import defaultdict

_PAGE_PATTERNS = [
    re.compile(r"^\d{1,4}$"),                          # 3
    re.compile(r"^page\s*\d{1,4}$", re.I),            # Page 3
    re.compile(r"^p\.\s*\d{1,4}$", re.I),             # p.3
    re.compile(r"^第\s*\d{1,4}\s*頁$"),               # 第3頁
    re.compile(r"^\d{1,4}\s*/\s*\d{1,4}$"),           # 3/10
    re.compile(r"^-\s*\d{1,4}\s*-$"),                 # - 3 -
]

def _is_page_marker(text: str) -> bool:
    t = text.strip()
    if len(t) > 30:
        return False
    return any(pat.match(t) for pat in _PAGE_PATTERNS)

def _normalize_for_repeat(text: str) -> str:
    # 將數字統一成 <NUM>，降低「Page 3 / Page 4」這種差異
    t = text.strip()
    t = re.sub(r"\d+", "<NUM>", t)
    t = re.sub(r"\s+", " ", t)
    return t.lower()

def remove_headers_footers(text_blocks: list[dict], repeat_ratio: float = 0.4, edge_ratio: float = 0.06) -> list[dict]:
    """
    移除 PDF 文字塊中的頁眉、頁腳和頁碼
    
    Args:
        text_blocks: 文字塊清單，每個 dict 包含 "page", "text", "bbox"
        repeat_ratio: 出現在 >= repeat_ratio * total_pages 的文字，視為頁眉頁腳候選（預設 0.4）
        edge_ratio: bbox 落在頁面頂/底 edge_ratio 的區域，視為頁眉頁腳候選（預設 0.06）
    
    Returns:
        清理後的文字塊清單
    """
    if not text_blocks:
        return text_blocks

    # 蒐集頁碼集合
    pages = sorted({b.get("page") for b in text_blocks if b.get("page") is not None})
    total_pages = len(pages)

    # 1) 跨頁重複統計（用 normalize 後的 key）
    occur_pages = defaultdict(set)  # norm_text -> set(pages)
    for b in text_blocks:
        p = b.get("page")
        txt = b.get("text", "")
        if p is None or not txt:
            continue
        key = _normalize_for_repeat(txt)
        # 太長的通常不是頁眉頁腳（但你可自行調整）
        if len(key) <= 120:
            occur_pages[key].add(p)

    repeat_keys = set()
    if total_pages >= 3:
        threshold = max(2, int(total_pages * repeat_ratio))
        for k, ps in occur_pages.items():
            if len(ps) >= threshold:
                repeat_keys.add(k)

    # 2) bbox 邊界判斷需要知道頁面高度範圍：我們用每頁 bbox 的 y 值估計
    # bbox 格式: [x1,y1,x2,y2]，我們取 y1,y2
    page_ymin = defaultdict(lambda: float("inf"))
    page_ymax = defaultdict(lambda: float("-inf"))

    for b in text_blocks:
        p = b.get("page")
        bb = b.get("bbox")
        if p is None or not (isinstance(bb, (list, tuple)) and len(bb) >= 4):
            continue
        y1, y2 = bb[1], bb[3]
        if isinstance(y1, (int, float)) and isinstance(y2, (int, float)):
            page_ymin[p] = min(page_ymin[p], y1, y2)
            page_ymax[p] = max(page_ymax[p], y1, y2)

    def _is_in_edge(b: dict) -> bool:
        p = b.get("page")
        bb = b.get("bbox")
        if p is None or not (isinstance(bb, (list, tuple)) and len(bb) >= 4):
            return False
        if page_ymin[p] == float("inf") or page_ymax[p] == float("-inf"):
            return False

        y_low = page_ymin[p]
        y_high = page_ymax[p]
        height = y_high - y_low
        if height <= 0:
            return False

        y1, y2 = bb[1], bb[3]
        y_min = min(y1, y2)
        y_max = max(y1, y2)

        top_cut = y_high - height * edge_ratio
        bot_cut = y_low + height * edge_ratio

        return (y_min >= top_cut) or (y_max <= bot_cut)

    # 3) 綜合判定
    cleaned = []
    for b in text_blocks:
        txt = (b.get("text") or "").strip()
        if not txt:
            continue

        # 規則：頁碼直接丟掉
        if _is_page_marker(txt):
            continue

        # 規則：跨頁重複 + 短字串 → 很可能是 header/footer
        key = _normalize_for_repeat(txt)
        if key in repeat_keys and len(txt) <= 120:
            continue

        # 規則：在頁面最上/最下 + 短字串 → 很可能是 header/footer
        if _is_in_edge(b) and len(txt) <= 120:
            continue

        cleaned.append(b)

    return cleaned
