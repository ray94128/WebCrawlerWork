# 店家評論爬蟲與分析系統 (WebCrawlerWork)

利用 Python 設計的自動化爬蟲程式，能自動收集 Google Maps 店家評論，並分析原因（關鍵字），生成專業的情緒評分視覺圖。

## 🚀 功能特點
- **自動爬蟲**: 使用 Selenium 模擬真實用戶操作，動態抓取評論。
- **情緒分析**: 整合 SnowNLP 分析每條評論的正負面情緒。
- **原因分析**: 提取熱門詞彙，快速掌握店家好評或負評的核心原因。
- **專業視覺化**: 採用 Plotly 生成互動式圖表，報表簡單明瞭。
- **簡單介面**: 基於 Streamlit 開發，使用者只需輸入網址即可一鍵分析。

## 🛠️ 安裝與使用

1. **安裝環境依賴**
   ```bash
   pip install -r requirements.txt
   ```

2. **啟動應用程式**
   ```bash
   streamlit run app.py
   ```

3. **操作步驟**
   - 打開 Google Maps 找到想分析的店家。
   - 點擊「評論」頁籤，複製當前網址。
   - 在本程式中輸入網址，點擊「開始分析」。

## 📂 檔案架構
- `app.py`: Streamlit 網頁介面主程式。
- `scraper.py`: Google Maps 爬蟲模組。
- `analyzer.py`: 情緒分析與視覺化模組。
- `requirements.txt`: 專案所需的套件清單。

## 🔗 GitHub
本專案已上傳至: [https://github.com/ray94128/WebCrawlerWork](https://github.com/ray94128/WebCrawlerWork)
