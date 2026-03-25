import requests
import re
import json

# 你的 Google Apps Script 網址
API_URL = "https://script.google.com/macros/s/AKfycbyVJt9fT7WBSbY0AOV07mluUv1bO2GJZ0usyfjtZClvaaSwfOSI3c-Qzn9a9uIYCmhNWQ/exec"
TARGET_URL = "https://kay-s-cut-0411yuna.streamlit.app/"

def run():
    # 模擬瀏覽器標頭，避免被網頁封鎖
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    try:
        response = requests.get(TARGET_URL, headers=headers, timeout=30)
        
        # 使用正則表達式抓取最新一筆紀錄，例如: [14:08:56] +20 (總銷量: 2141)
        # 此格式對應目標網頁的「即時變動紀錄」區塊
        pattern = r"\[(\d{2}:\d{2}:\d{2})\]\s*([+-]\d+)\s*\(總銷量:\s*(\d+)\)"
        match = re.search(pattern, response.text)

        if match:
            time_val = match.group(1)
            diff_raw = match.group(2)
            total_sales = match.group(3)
            
            # 處理數據：拿掉 + 號，保留數字
            diff_clean = diff_raw.replace("+", "")
            
            # 依照你的試算表格式準備資料：時刻, 總庫存, 總銷量, 差值
            payload = {
                "time": time_val,
                "totalSales": total_sales,
                "diff": diff_clean,
                "stock": 8000 - int(total_sales) # 假設初始總庫存為 8000
            }
            
            # 傳送到 Google 試算表
            res = requests.post(API_URL, data=json.dumps(payload))
            print(f"成功抓取並傳送: {time_val}, 銷量變動: {diff_clean}, 狀態: {res.text}")
        else:
            print("目前網頁上沒有偵測到符合格式的數據紀錄")
            
    except Exception as e:
        print(f"發生錯誤: {e}")

if __name__ == "__main__":
    run()
