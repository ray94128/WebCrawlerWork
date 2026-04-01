from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import pandas as pd

class GoogleMapsScraper:
    def __init__(self, headless=True):
        self.options = Options()
        if headless:
            self.options.add_argument("--headless")
        self.options.add_argument("--no-sandbox")
        self.options.add_argument("--disable-dev-shm-usage")
        self.options.add_argument("--lang=zh-TW") # 設定語系
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=self.options)

    def scrape_reviews(self, url, max_reviews=50):
        self.driver.get(url)
        time.sleep(5) # 等待頁面加載

        reviews_data = []
        try:
            # 找到捲動區域 (評論欄位)
            # 嘗試找包含評論的捲動容器
            scrollable_div = self.driver.find_element(By.XPATH, '//div[@role="main"]//div[contains(@class, "m67Hec")]')
            
            last_height = self.driver.execute_script("return arguments[0].scrollHeight", scrollable_div)
            
            while len(reviews_data) < max_reviews:
                # 捲動到最底部
                self.driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scrollable_div)
                time.sleep(2)
                
                # 取得當前載入的評論
                review_elements = self.driver.find_elements(By.XPATH, '//div[contains(@class, "jfti7")]')
                
                for element in review_elements:
                    if len(reviews_data) >= max_reviews:
                        break
                        
                    try:
                        # 評論內容
                        text_element = element.find_elements(By.XPATH, './/span[contains(@class, "wiI7pd")]')
                        text = text_element[0].text if text_element else ""
                        
                        # 評分 (星等)
                        rating_element = element.find_element(By.XPATH, './/span[contains(@class, "kv9pPn")]')
                        rating = float(rating_element.text.split(" ")[0]) if rating_element else 0.0
                        
                        # 避免重複抓取
                        if {"review": text, "rating": rating} not in reviews_data:
                            reviews_data.append({"review": text, "rating": rating})
                    except Exception as e:
                        continue
                
                # 檢查是否還有更多評論 (高度是否不再增加)
                new_height = self.driver.execute_script("return arguments[0].scrollHeight", scrollable_div)
                if new_height == last_height:
                    break
                last_height = new_height
                
        except Exception as e:
            print(f"Error during scraping: {e}")
        finally:
            self.driver.quit()
            
        return pd.DataFrame(reviews_data)

if __name__ == "__main__":
    # 測試程式碼
    scraper = GoogleMapsScraper(headless=True)
    test_url = "https://www.google.com/maps/place/%E9%BC%8E%E6%B3%B0%E8%B1%90+%E4%BF%A1%E7%BE%A9%E5%BA%97/@25.03337,121.52988,17z/data=!4m7!3m6!1s0x3442a99187123999:0x8798993952f01f05!8m2!3d25.03337!4d121.52988!9m1!1b1!16s%2Fg%2F1tcx3_d9?entry=ttu"
    df = scraper.scrape_reviews(test_url, max_reviews=10)
    print(df)
