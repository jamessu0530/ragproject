# 網頁事實查核系統

基於 RAG 技術的本地化網頁事實查核系統，使用 Ollama 本地 LLM。

## 功能

- 抓取網頁內容並向量化
- 使用 Pinecone 進行向量檢索
- 使用 Cohere 進行重排序
- 使用本地 Gemma3 模型生成回答

## 環境變數

在 `.env` 檔案中設定：

```
PINECONE_API_KEY=你的_pinecone_api_key
PINECONE_INDEX=medical-fact-checker
GOOGLE_API_KEY=你的_google_api_key
COHERE_API_KEY=你的_cohere_api_key
```

## 安裝與執行

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python src/main_checker.py
```

## 使用方式

1. 輸入網址，系統會自動抓取並索引
2. 輸入問題，系統會根據網頁內容回答
