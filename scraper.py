from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
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
        
        # 雲端環境穩定性必要參數
        self.options.add_argument("--no-sandbox")
        self.options.add_argument("--disable-dev-shm-usage")
        self.options.add_argument("--disable-gpu")
        self.options.add_argument("--window-size=1920,1080")
        self.options.add_argument("--lang=zh-TW")
        self.options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        # 嘗試在 Streamlit Cloud (Linux) 與本地 Windows 之間尋找最佳啟動方式
        try:
            # 如果在 Streamlit Cloud 上，會自動安裝到 /usr/bin/chromium
            import os
            if os.path.exists("/usr/bin/chromium"):
                self.options.binary_location = "/usr/bin/chromium"
            
            # 優先嘗試使用已在系統路徑中的 driver
            self.driver = webdriver.Chrome(options=self.options)
        except Exception:
            # 如果失敗，再退回使用 ChromeDriverManager 自動安裝 (適用於本地 Windows)
            try:
                self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=self.options)
            except Exception as e:
                print(f"Failed to initialize WebDriver: {e}")
                raise e

    def scrape_reviews(self, url, max_reviews=50):
        self.driver.get(url)
        time.sleep(8)

        reviews_data = []
        try:
            # 1. 尋找捲動容器
            scrollable_div = None
            # 根據 debug_page.html，評論通常在 role="main" 的 div 裡面
            try:
                # 嘗試定位評論專用的捲動區域
                wait = WebDriverWait(self.driver, 10)
                scrollable_div = wait.until(EC.presence_of_element_located((By.XPATH, '//div[@role="main" and @tabindex="-1"]')))
            except:
                # 備用定位
                selectors = ['//div[contains(@class, "m67Hec")]', '//div[@role="main"]', '//div[@id="pane"]']
                for s in selectors:
                    try:
                        scrollable_div = self.driver.find_element(By.XPATH, s)
                        if scrollable_div: break
                    except: continue

            if not scrollable_div:
                print("Could not find scrollable container.")
                return pd.DataFrame()

            # 2. 開始捲動與抓取
            last_height = self.driver.execute_script("return arguments[0].scrollHeight", scrollable_div)
            
            for _ in range(20): # 限制捲動次數
                # 取得目前所有的評論容器
                elements = self.driver.find_elements(By.XPATH, '//div[@data-review-id]')
                
                for element in elements:
                    if len(reviews_data) >= max_reviews:
                        break
                    
                    try:
                        # 評論內容
                        text = ""
                        text_elements = element.find_elements(By.XPATH, './/span[@class="wiI7pd"]')
                        if text_elements:
                            text = text_elements[0].text
                        
                        # 如果沒文字，找 MyEned 下的 span
                        if not text:
                            text_elements = element.find_elements(By.XPATH, './/div[contains(@class, "MyEned")]//span')
                            if text_elements:
                                text = text_elements[0].text

                        # 評分
                        rating = 0.0
                        # 尋找包含星等的 span，通常有 aria-label
                        star_elements = element.find_elements(By.XPATH, './/*[contains(@aria-label, "星")]')
                        if star_elements:
                            label = star_elements[0].get_attribute("aria-label")
                            import re
                            # 提取數字 (例如 "5 顆星" -> 5, "4.5 stars" -> 4.5)
                            match = re.search(r"(\d+(\.\d+)?)", label)
                            if match:
                                rating = float(match.group(1))
                        
                        if text and not any(r['review'] == text for r in reviews_data):
                            reviews_data.append({"review": text, "rating": rating})
                    except:
                        continue
                
                if len(reviews_data) >= max_reviews:
                    break
                
                # JavaScript 捲動
                self.driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scrollable_div)
                time.sleep(3)
                
                new_height = self.driver.execute_script("return arguments[0].scrollHeight", scrollable_div)
                if new_height == last_height:
                    break
                last_height = new_height

        except Exception as e:
            print(f"Error: {e}")
        finally:
            self.driver.quit()
            
        return pd.DataFrame(reviews_data)

if __name__ == "__main__":
    # 測試程式碼
    scraper = GoogleMapsScraper(headless=True)
    test_url = "https://www.google.com/maps/place/7-ELEVEN+%E4%B8%B9%E8%81%AF%E9%96%80%E5%B8%82/@24.2480998,120.5595681,16z/data=!4m8!3m7!1s0x346915160a647be7:0x2f17756bc4419c8c!8m2!3d24.2504142!4d120.5658248!9m1!1b1!16s%2Fg%2F11p6wlj51c?entry=ttu&g_ep=EgoyMDI2MDMyOS4wIKXMDSoASAFQAw%3D%3D"
    df = scraper.scrape_reviews(test_url, max_reviews=10)
    print("抓取結果:")
    print(df)
