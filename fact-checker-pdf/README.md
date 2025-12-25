# PDF 事實查核系統

基於 RAG 技術的 PDF 文件事實查核系統，使用 Ollama 本地 LLM。

## 功能

- 讀取 PDF 檔案並向量化
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
python src/main_checkerpdfmod.py
```

## 使用方式

1. 將 PDF 檔案放入 `pdfs/` 資料夾
2. 執行程式，系統會自動讀取並索引所有 PDF
3. 輸入問題，系統會根據 PDF 內容回答
