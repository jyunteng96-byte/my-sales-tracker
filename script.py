import time
import json
import requests
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 請確保這是你最新的 Apps Script 網址
API_URL = "https://script.google.com/macros/s/AKfycbyVJt9fT7WBSbY0AOV07mluUv1bO2GJZ0usyfjtZClvaaSwfOSI3c-Qzn9a9uIYCmhNWQ/exec"
TARGET_URL = "https://kay-s-cut-0411yuna.streamlit.app/"

def run():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        print("🚀 開始執行深度抓取...")
        driver.get(TARGET_URL)
        
        # 關鍵修改：等待 Streamlit 的主要內容容器出現
        print("⏳ 等待數據加載中...")
        wait = WebDriverWait(driver, 60) # 最多等一分鐘
        
        # 循環檢查頁面內容，直到找到包含 "總銷量" 的文字
        found = False
        for i in range(12): # 每 5 秒檢查一次，共檢查一分鐘
            body_text = driver.find_element(By.TAG_NAME, "body").text
            # 搜尋格式範例：[16:04:01] +20 (總銷量: 2676)
            pattern = r"\[(\d{2}:\d{2}:\d{2})\]\s*([+-]\d+)\s*\(總銷量:\s*(\d+)\)"
            match = re.search(pattern, body_text)
            
            if match:
                payload = {
                    "time": match.group(1),
                    "diff": match.group(2).replace("+", ""),
                    "totalSales": match.group(3),
                    "stock": 8000 - int(match.group(3))
                }
                print(f"🎯 成功鎖定數據: {payload}")
                
                # 傳送資料到 Google 試算表
                res = requests.post(API_URL, data=json.dumps(payload), timeout=20)
                print(f"📡 試算表回傳: {res.text}")
                found = True
                break
            else:
                print(f"第 {i+1} 次嘗試：數據尚未載入，稍候再試...")
                time.sleep(5)

        if not found:
            print("❌ 失敗：已等待一分鐘，網頁仍未顯示銷量紀錄。")

    except Exception as e:
        print(f"⚠️ 運行出錯: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    run()
