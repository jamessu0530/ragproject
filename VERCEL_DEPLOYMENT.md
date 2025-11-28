# Vercel 部署指南

## 1. 安裝 Vercel CLI

```bash
npm i -g vercel
```

## 2. 設定環境變數

在 Vercel Dashboard 或使用 CLI 設定：

```bash
vercel env add PINECONE_API_KEY
vercel env add PINECONE_INDEX
vercel env add GOOGLE_API_KEY
vercel env add PRODUCT_API_BASE_URL
vercel env add AUTO_INIT  # 建議設為 "False"
vercel env add CORS_ORIGINS  # 設定您的前端網域
```

或在 Vercel Dashboard: Settings → Environment Variables

## 3. 部署

```bash
vercel
```

或直接推送到 GitHub，Vercel 會自動部署。

## 4. 初始化資料庫

部署完成後，手動觸發初始化：

```bash
curl -X POST https://your-app.vercel.app/api/init
```

## 5. 測試 API

```bash
curl -X POST https://your-app.vercel.app/api/search \
     -H "Content-Type: application/json" \
     -d '{"query": "我要找手機"}'
```

## 注意事項

1. **Serverless 限制**：Vercel 使用 Serverless Functions，每次請求可能在不同實例執行
2. **冷啟動**：首次請求可能較慢（約 1-2 秒）
3. **執行時間限制**：免費版單次請求最多 10 秒，付費版可到 60 秒
4. **初始化策略**：建議 `AUTO_INIT=False`，改用手動觸發 `/api/init`
5. **環境變數**：務必在 Vercel Dashboard 設定所有必要的環境變數

