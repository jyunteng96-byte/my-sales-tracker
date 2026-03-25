import time
import json
import requests
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

API_URL = "https://script.google.com/macros/s/AKfycbyVJt9fT7WBSbY0AOV07mluUv1bO2GJZ0usyfjtZClvaaSwfOSI3c-Qzn9a9uIYCmhNWQ/exec"
TARGET_URL = "https://kay-s-cut-0411yuna.streamlit.app/"

def run():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    # 加入偽裝特徵，讓網頁以為是普通電腦
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        print("🚀 啟動深度模擬模式...")
        driver.get(TARGET_URL)
        
        # 增加初始等待時間
        time.sleep(20) 
        
        found = False
        for i in range(15): # 延長檢查到 15 次
            # 獲取完整 HTML，這樣連隱藏的數據都能搜到
            html_source = driver.page_source
            body_text = driver.find_element(By.TAG_NAME, "body").text
            
            # 同時搜尋文字內容與 HTML 原始碼
            pattern = r"\[(\d{2}:\d{2}:\d{2})\]\s*([+-]\d+)\s*\(總銷量:\s*(\d+)\)"
            match = re.search(pattern, body_text) or re.search(pattern, html_source)
            
            if match:
                payload = {
                    "time": match.group(1),
                    "diff": match.group(2).replace("+", ""),
                    "totalSales": match.group(3),
                    "stock": 8000 - int(match.group(3))
                }
                print(f"🎯 成功！抓到數據: {payload}")
                
                # 傳送並印出結果
                res = requests.post(API_URL, data=json.dumps(payload), timeout=20)
                print(f"📡 試算表同步狀態: {res.text}")
                found = True
                break
            else:
                # 模擬輕微滾動，觸發 Streamlit 載入
                driver.execute_script("window.scrollTo(0, 500);")
                print(f"第 {i+1} 次嘗試：等待數據渲染中...")
                time.sleep(10) # 每次等 10 秒

        if not found:
            print("❌ 最終失敗：網頁在雲端環境不顯示數據。")

    except Exception as e:
        print(f"⚠️ 異常: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    run()
