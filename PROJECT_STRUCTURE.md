# 專案結構說明

專案已分離為三個獨立的子專案，每個專案都有獨立的環境變數和依賴管理。

## 專案結構

```
ragproject/
├── rag-api/                    # RAG 產品搜尋 API
│   ├── src/
│   │   └── app.py              # Flask API 主程式
│   ├── NTOUutils/              # 產品搜尋相關工具
│   ├── utils/                  # 共用工具（embedding, pinecone）
│   ├── scripts/                # 資料處理腳本
│   ├── .env                    # rag-project index 專用
│   ├── requirements.txt
│   └── README.md
│
├── fact-checker-web/           # 網頁事實查核
│   ├── src/
│   │   └── main_checker.py    # 主程式
│   ├── utils/                  # 共用工具
│   ├── scripts/                # 初始化腳本
│   ├── .env                    # medical-fact-checker index 專用
│   ├── requirements.txt
│   └── README.md
│
├── fact-checker-pdf/           # PDF 事實查核
│   ├── src/
│   │   └── main_checkerpdfmod.py  # 主程式
│   ├── utils/                  # 共用工具（含 pdf_utils）
│   ├── scripts/                # 初始化腳本
│   ├── pdfs/                   # PDF 檔案存放處
│   ├── .env                    # medical-fact-checker index 專用
│   ├── requirements.txt
│   └── README.md
│
└── [舊檔案保留在原位置，可選擇性刪除]
```

## 各專案說明

### rag-api
- **用途**: 產品語意搜尋 API + 訊息潤飾 API
- **Pinecone Index**: `rag-project`
- **主要功能**:
  - `/api/search` - 產品搜尋
  - `/api/rewrite` - 訊息潤飾

### fact-checker-web
- **用途**: 網頁內容事實查核
- **Pinecone Index**: `medical-fact-checker`
- **主要功能**: 抓取網頁、向量化、問答

### fact-checker-pdf
- **用途**: PDF 文件事實查核
- **Pinecone Index**: `medical-fact-checker`
- **主要功能**: 讀取 PDF、向量化、問答

## 使用方式

每個專案都是獨立的，可以分別執行：

```bash
# RAG API
cd rag-api
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python src/app.py

# 網頁事實查核
cd fact-checker-web
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python src/main_checker.py

# PDF 事實查核
cd fact-checker-pdf
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python src/main_checkerpdfmod.py
```

## 注意事項

- 每個專案都有獨立的 `.env` 檔案，互不干擾
- 每個專案的 `requirements.txt` 只包含該專案需要的套件
- 舊的檔案結構保留在原位置，可以選擇性刪除或保留作為備份
