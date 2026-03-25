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
        print("🚀 啟動強化版抓取模式...")
        driver.get(TARGET_URL)
        
        # 使用 WebDriverWait 等待特定數據容器出現，而不是死等 30 秒
        wait = WebDriverWait(driver, 45)
        print("⏳ 等待 Streamlit 組件渲染...")
        
        # 嘗試尋找包含即時變動紀錄的元素
        time.sleep(20) # 給予基礎緩衝
        
        # 獲取渲染後的完整 HTML 內容
        html_content = driver.page_source
        
        # 修改正則表達式，適應可能存在的 HTML 標籤干擾
        # 這裡針對 [16:04:01] +20 (總銷量: 2676) 進行匹配
        pattern = r"\[(\d{2}:\d{2}:\d{2})\]\s*([+-]\d+)\s*\(總銷量:\s*(\d+)\)"
        matches = re.findall(pattern, html_content)

        if matches:
            # 抓取最後一筆紀錄 (即最新的那一行)
            latest = matches[0]
            payload = {
                "time": latest[0],
                "diff": latest[1].replace("+", ""),
                "totalSales": latest[2],
                "stock": 8000 - int(latest[2])
            }
            print(f"🎯 成功鎖定數據: {payload}")
            
            res = requests.post(API_URL, data=json.dumps(payload), timeout=15)
            print(f"📡 試算表同步結果: {res.text}")
        else:
            print("❌ 關鍵字搜尋失敗。目前網頁上的純文字內容為：")
            print(driver.find_element(By.TAG_NAME, "body").text[:500])

    except Exception as e:
        print(f"⚠️ 運行中斷: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    run()
