import requests
import re
import json

# 你的 Google Apps Script 網址
API_URL = "https://script.google.com/macros/s/AKfycbyVJt9fT7WBSbY0AOV07mluUv1bO2GJZ0usyfjtZClvaaSwfOSI3c-Qzn9a9uIYCmhNWQ/exec"
TARGET_URL = "https://kay-s-cut-0411yuna.streamlit.app/"

def fetch_data():
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        # 增加超時設定，避免雲端卡死
        response = requests.get(TARGET_URL, headers=headers, timeout=30)
        content = response.text
        
        # 抓取最新一筆記錄：[時間] +變動 (總銷量: 數字)
        pattern = r"\[(\d{2}:\d{2}:\d{2})\]\s*([+-]\d+)\s*\(總銷量:\s*(\d+)\)"
        match = re.search(pattern, content)
        
        if match:
            time_val = match.group(1)
            diff_val = match.group(2).replace("+", "")
            total_val = match.group(3)
            stock_val = 8000 - int(total_val) # 庫存假設 8000

            payload = {
                "time": time_val,
                "stock": stock_val,
                "totalSales": total_val,
                "diff": diff_val
            }
            
            # 傳送到 Google Apps Script
            res = requests.post(API_URL, data=json.dumps(payload))
            print(f"成功傳送資料: {time_val}, 銷量: {total_val}")
        else:
            print("無法解析數據，Streamlit 內容可能尚未載入。")
            
    except Exception as e:
        print(f"執行錯誤: {e}")

if __name__ == "__main__":
    fetch_data()
