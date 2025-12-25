# RAG API - 產品搜尋服務

基於向量檢索的產品語意搜尋 API，使用 Flask 框架建構。

## 功能

- 產品語意搜尋 (`/api/search`)
- 訊息禮貌潤飾 (`/api/rewrite`)

## 環境變數

在 `.env` 檔案中設定：

```
PINECONE_API_KEY=你的_pinecone_api_key
PINECONE_INDEX=rag-project
GOOGLE_API_KEY=你的_google_api_key
PORT=5001
```

## 安裝與執行

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python src/app.py
```

## API 端點

### POST `/api/search`

搜尋與查詢語句相關的產品。

**Request:**
```json
{"query": "我想買零食"}
```

**Response:**
```json
["product_id_1", "product_id_2", "product_id_3"]
```

### POST `/api/rewrite`

使用本地 Gemma3 模型潤飾訊息。

**Request:**
```json
{"message": "原始訊息"}
```

**Response:**
```json
{
  "original": "原始訊息",
  "polished": "潤飾後的訊息"
}
```
