import time
import json
import requests
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

# 請確認這個網址是「管理部署」中最新的「網頁應用程式」網址
API_URL = "https://script.google.com/macros/s/AKfycbyVJt9fT7WBSbY0AOV07mluUv1bO2GJZ0usyfjtZClvaaSwfOSI3c-Qzn9a9uIYCmhNWQ/exec"
TARGET_URL = "https://kay-s-cut-0411yuna.streamlit.app/"

def run():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    # 模擬真人瀏覽器標頭
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        print("🚀 正在啟動雲端瀏覽器...")
        driver.get(TARGET_URL)
        
        # 增加等待時間到 30 秒，確保 Streamlit 跑完
        print("⏳ 等待網頁渲染中 (30秒)...")
        time.sleep(30) 

        # 抓取整個頁面的內容
        body_text = driver.find_element(By.TAG_NAME, "body").text
        
        # 搜尋格式：[16:04:01] +20 (總銷量: 2676)
        pattern = r"\[(\d{2}:\d{2}:\d{2})\]\s*([+-]\d+)\s*\(總銷量:\s*(\d+)\)"
        match = re.search(pattern, body_text)

        if match:
            payload = {
                "time": match.group(1),
                "diff": match.group(2).replace("+", ""),
                "totalSales": match.group(3),
                "stock": 8000 - int(match.group(3))
            }
            print(f"🎯 成功抓到數據: {payload}")
            
            # 傳送資料
            res = requests.post(API_URL, data=json.dumps(payload), timeout=15)
            print(f"📡 試算表端回傳內容: {res.text}")
        else:
            print("❌ 失敗：在網頁上找不到符合格式的銷量紀錄。")
            print("--- 網頁內容片段 ---")
            print(body_text[:1000]) # 印出內容幫助除錯
            print("------------------")

    except Exception as e:
        print(f"⚠️ 發生錯誤: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    run()
