# PDF 事實查核系統

基於 RAG 技術的 PDF 文件事實查核系統，使用 Ollama 本地 LLM。

## 功能特色

### 核心功能
- 📄 智能 PDF 讀取與向量化
- 🔍 使用 Pinecone 進行向量檢索
- 🎯 使用 Cohere 進行重排序
- 🤖 使用本地 Gemma3 模型生成回答

### 文字處理優化
- ✨ **注音符號過濾**：自動移除 ㄅㄆㄇㄈ 等注音符號
- 🧹 **文字正規化**：移除多餘換行和空白
- 🚫 **頁碼過濾**：自動過濾獨立的頁碼數字
- 📊 **類型識別**：保留文件結構資訊（Title, NarrativeText 等）

### RAG 技術棧
- **提取 (Extraction)**：使用 `unstructured` 庫，支援 OCR fallback
- **分塊 (Chunking)**：智能 block-based chunking，保留頁碼與類型資訊
- **嵌入 (Embedding)**：Google Gemini `text-embedding-004`
- **檢索 (Retrieval)**：Pinecone 向量資料庫
- **重排序 (Reranking)**：Cohere Rerank API
- **生成 (Generation)**：Ollama Gemma3:4b

## 環境變數

在 `.env` 檔案中設定：

```env
PINECONE_API_KEY=你的_pinecone_api_key
PINECONE_INDEX=medical-fact-checker
GOOGLE_API_KEY=你的_google_api_key
COHERE_API_KEY=你的_cohere_api_key
```

## 安裝與執行

### 1. 建立虛擬環境並安裝依賴

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. 建立 Pinecone Index（首次執行）

```bash
python scripts/index.py
```

### 3. 準備 PDF 檔案

將 PDF 檔案放入 `pdfs/` 資料夾

### 4. 執行主程式

```bash
python src/main_checkerpdfmod.py
```

## 實用工具腳本

### 清除 Pinecone 資料

```bash
python scripts/clear_pinecone.py
```

### 測試提取結果

查看 PDF 提取的詳細資訊：

```bash
python scripts/test_extract.py
```

輸出到檔案方便查看：

```bash
python scripts/test_extract.py > extract_output.txt
```

## 系統架構

```
PDF 檔案
    ↓
[Extract] unstructured → Text Blocks (含 page, type, text)
    ↓
[Clean] 移除注音、換行、頁碼
    ↓
[Chunk] 智能分塊 (900 字元上限)
    ↓
[Embed] Google Gemini Embedding
    ↓
[Store] Pinecone Vector DB
    ↓
[Query] 使用者問題 → Embedding
    ↓
[Retrieve] Top-K 檢索 (k=20)
    ↓
[Rerank] Cohere Rerank (取 Top-3)
    ↓
[Generate] Ollama Gemma3 生成回答
```

## 專案結構

```
fact-checker-pdf/
├── pdfs/                   # PDF 檔案資料夾
├── scripts/
│   ├── index.py           # 建立 Pinecone index
│   ├── clear_pinecone.py  # 清除資料
│   └── test_extract.py    # 測試提取功能
├── src/
│   └── main_checkerpdfmod.py  # 主程式
├── utils/
│   ├── chunking_utils.py      # 分塊邏輯
│   ├── embedding_utils.py     # Embedding API
│   ├── pinecone_utils.py      # Pinecone 連線
│   ├── rerank_utils.py        # Cohere Rerank
│   └── pdf_utils/
│       ├── extract.py         # PDF 提取 + 清理
│       └── upsert.py          # 向量化 + 上傳
├── .env                   # 環境變數設定
└── requirements.txt       # Python 依賴
```

## 技術細節

### Chunking 策略
- **大小限制**：900 字元上限
- **邊界對齊**：嚴格按 block 邊界切分，不會切斷語意
- **Metadata 保留**：每個 chunk 包含 `pages`（頁碼列表）、`types`（類型列表）

### 文字清理
- 移除注音符號（Unicode U+3105-U+312F）
- 正規化所有空白字元
- 過濾純數字頁碼（≤ 4 位數）

## 注意事項

- 確保 Ollama 已安裝且 `gemma3:4b` 模型已下載
- Pinecone index 維度必須設為 768（對應 Gemini Embedding）
- 建議先測試單一 PDF 確認流程正常
