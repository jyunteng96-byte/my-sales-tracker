import time
import json
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

API_URL = "https://script.google.com/macros/s/AKfycbyVJt9fT7WBSbY0AOV07mluUv1bO2GJZ0usyfjtZClvaaSwfOSI3c-Qzn9a9uIYCmhNWQ/exec"
TARGET_URL = "https://kay-s-cut-0411yuna.streamlit.app/"

def run():
    chrome_options = Options()
    chrome_options.add_argument("--headless") # 無頭模式，不開啟視窗
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        driver.get(TARGET_URL)
        print("等待網頁加載 15 秒...")
        time.sleep(15) # 等待 Streamlit 渲染數據

        # 抓取頁面上的所有文字
        page_text = driver.find_element(By.TAG_NAME, "body").text
        
        import re
        # 搜尋最新的一筆紀錄：[時間] +變動 (總銷量: 數字)
        pattern = r"\[(\d{2}:\d{2}:\d{2})\]\s*([+-]\d+)\s*\(總銷量:\s*(\d+)\)"
        match = re.search(pattern, page_text)

        if match:
            payload = {
                "time": match.group(1),
                "diff": match.group(2).replace("+", ""), # 拿掉加號
                "totalSales": match.group(3),
                "stock": 8000 - int(match.group(3))
            }
            res = requests.post(API_URL, data=json.dumps(payload))
            print(f"✅ 抓取成功！數據時間: {match.group(1)}, 銷量: {match.group(3)}, 回應: {res.text}")
        else:
            print("❌ 依然抓不到數據。網頁文字片段如下：")
            print(page_text[:500])

    except Exception as e:
        print(f"⚠️ 發生錯誤: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    run()
