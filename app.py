import streamlit as st
import pandas as pd
from scraper import GoogleMapsScraper
from analyzer import ReviewAnalyzer

# 設定頁面配置
st.set_page_config(page_title="店家評論分析工具", layout="wide")

st.title("🏙️ 店家評論爬蟲與分析工具")
st.markdown("輸入 Google Maps 店家連結，自動收集評論並分析情緒與熱門詞彙。")

# 側邊欄：設定
with st.sidebar:
    st.header("⚙️ 設定")
    max_reviews = st.slider("最大抓取評論數", 10, 200, 50)
    headless = st.checkbox("無頭模式 (較快)", value=True)

# 主區域：輸入
url = st.text_input("🔗 請輸入 Google Maps 店家連結:", placeholder="https://www.google.com/maps/place/...")

if st.button("🚀 開始分析"):
    if not url:
        st.error("請提供有效的網址。")
    else:
        with st.status("正在執行中...", expanded=True) as status:
            st.write("正在啟動爬蟲工具...")
            scraper = GoogleMapsScraper(headless=headless)
            
            st.write(f"正在抓取 Google Maps 評論 (預計抓取 {max_reviews} 條)...")
            df = scraper.scrape_reviews(url, max_reviews=max_reviews)
            
            if df.empty:
                st.error("未能抓取到任何評論，請確認網址是否正確。")
                status.update(label="執行失敗", state="error")
            else:
                st.write(f"成功抓取 {len(df)} 條評論，正在進行分析...")
                analyzer = ReviewAnalyzer(df)
                df = analyzer.analyze_sentiment()
                
                status.update(label="完成！", state="complete", expanded=False)

                # 顯示結果
                st.divider()
                st.header("📊 分析報表")
                
                # 第一排：視覺化圖表
                col1, col2 = st.columns(2)
                with col1:
                    st.plotly_chart(analyzer.plot_sentiment_distribution(), use_container_width=True)
                with col2:
                    st.plotly_chart(analyzer.plot_rating_distribution(), use_container_width=True)
                
                # 第二排：原因分析 (關鍵字)
                st.divider()
                st.header("🔍 原因分析 (熱門詞彙)")
                
                pos_col, neg_col = st.columns(2)
                with pos_col:
                    st.subheader("🟢 正面評價提到的關鍵字")
                    pos_keywords = analyzer.get_keywords(sentiment='正向')
                    if pos_keywords:
                        st.write(", ".join(pos_keywords))
                    else:
                        st.write("尚無足夠數據。")
                        
                with neg_col:
                    st.subheader("🔴 負面評價提到的關鍵字")
                    neg_keywords = analyzer.get_keywords(sentiment='負向')
                    if neg_keywords:
                        st.write(", ".join(neg_keywords))
                    else:
                        st.write("尚無足夠數據。")

                # 第三排：原始數據
                st.divider()
                with st.expander("📄 查看原始資料"):
                    st.dataframe(df, use_container_width=True)
                    st.download_button(
                        label="下載數據 (CSV)",
                        data=df.to_csv(index=False).encode('utf-8-sig'),
                        file_name="reviews_analysis.csv",
                        mime="text/csv",
                    )
