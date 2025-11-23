# Local RAG & Web Fact Checker 🕵️‍♂️

這是一個基於 **RAG (Retrieval-Augmented Generation)** 技術的本地化事實查核系統。
它能夠抓取指定的網頁內容，將其向量化並存入資料庫，接著利用本地的 LLM (Ollama) 根據該網頁內容回答你的問題。

## ✨ 功能特色

- **隱私安全**：使用本地 LLM (`gemma3:4b` via Ollama)，資料不需傳送給 OpenAI。
- **即時查核**：輸入任意網址 (如新聞、醫療文章)，即時建立索引並進行問答。
- **高精準度**：
  - **Embedding**: 使用 **Google Gemini (`text-embedding-004`)** 進行高品質向量化 (維度 768)。
  - **Rerank**: 使用 `BAAI/bge-reranker-base` 進行二次重排序，確保 AI 看到最相關的片段。
- **向量資料庫**: 使用 Pinecone 儲存與檢索向量資料。

## 🛠️ 安裝需求

1. **Python 3.10+**
2. **Ollama** (需安裝並下載模型)
   ```bash
   ollama pull gemma3:4b
   ```
3. **Pinecone API Key** (請至 Pinecone 官網申請免費 Key)
4. **Google API Key** (用於產生 Embedding，請至 Google AI Studio 申請)

## 🚀 快速開始

### 1. 設定環境

複製 `.env.example` (如果有) 或直接建立 `.env` 檔案：
```bash
PINECONE_API_KEY=你的_pinecone_api_key
PINECONE_INDEX=你的_index_name
GOOGLE_API_KEY=你的_google_api_key
```

安裝 Python 套件：
```bash
python -m venv venv
source venv/bin/activate
# 安裝必要套件:
pip install pinecone google-generativeai sentence-transformers requests beautifulsoup4 python-dotenv ollama
```

### 2. 建立資料庫索引 (第一次使用時)

執行 `index.py` 來建立 Pinecone Index (維度 768)：
```bash
python index.py
```

### 3. 啟動網頁查核機器人

這是本專案的核心功能。執行後，輸入你想查核的網址即可開始對話：
```bash
python main_checker.py
```

**使用範例：**
1. 輸入網址：`https://www.cdc.gov/flu/symptoms/coldflu.htm` (CDC 感冒與流感資訊)
2. 程式會自動抓取、切片並存入資料庫。
3. 詢問問題：`請問感冒和流感的主要差別是什麼？`
4. 系統會根據網頁內容生成回答。

## 📂 檔案說明

- **`main_checker.py`**: **[主程式]** 互動式網頁抓取與問答機器人。
- **`embedding_utils.py`**: 封裝 Google Gemini Embedding API 的共用工具。
- **`rag_retrieve.py`**: RAG 流程的核心邏輯 (Retrieve -> Rerank -> Generate) 測試腳本。
- **`upsert_vectors.py`**: 手動將資料寫入資料庫的腳本 (範例)。
- **`index.py`**: 用於建立 Pinecone Index 的工具腳本。
- **`query_vectors.py`**: 單純測試向量搜尋功能的腳本。

## ⚠️ 注意事項

- 本專案使用 **CrossEncoder** 進行重排序，第一次執行時會自動下載模型 (約 500MB+)，請耐心等候。
- 網頁抓取功能依賴 `requests` 與 `BeautifulSoup`，對於動態渲染 (JavaScript) 的網站可能無法完整抓取。
