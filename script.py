import requests
import json
import time

# 你的 Google Apps Script 網址
API_URL = "https://script.google.com/macros/s/AKfycbyVJt9fT7WBSbY0AOV07mluUv1bO2GJZ0usyfjtZClvaaSwfOSI3c-Qzn9a9uIYCmhNWQ/exec"
# Streamlit 網頁背後的真實數據接口 (由網頁原始碼解析得出)
DATA_URL = "https://kay-s-cut-0411yuna.streamlit.app/~/+/events"

def run():
    print("🚀 啟動 API 直連模式...")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': '*/*',
        'Content-Type': 'text/plain;charset=UTF-8',
        'Origin': 'https://kay-s-cut-0411yuna.streamlit.app'
    }

    try:
        # 向 Streamlit 請求最新的狀態快照
        response = requests.get("https://kay-s-cut-0411yuna.streamlit.app/~/+/healthz")
        if response.status_code == 200:
            # 由於 Streamlit 的數據結構較複雜，我們改抓取網頁主要標籤中的快照數據
            # 如果直接抓取失敗，我們使用最原始的 requests 配合結構化搜索
            page = requests.get("https://kay-s-cut-0411yuna.streamlit.app/", headers=headers)
            content = page.text
            
            import re
            # 搜尋格式範例：[16:04:01] +20 (總銷量: 2676)
            # 這次加上預防轉義字元的處理
            pattern = r"\\\[(\d{2}:\d{2}:\d{2})\\\]\s*([\+\-]\d+)\s*\(總銷量:\s*(\d+)\)"
            match = re.search(pattern, content)
            
            if not match:
                # 嘗試第二次搜尋 (非轉義格式)
                pattern = r"\[(\d{2}:\d{2}:\d{2})\]\s*([+-]\d+)\s*\(總銷量:\s*(\d+)\)"
                match = re.search(pattern, content)

            if match:
                payload = {
                    "time": match.group(1),
                    "diff": match.group(2).replace("+", ""),
                    "totalSales": match.group(3),
                    "stock": 8000 - int(match.group(3))
                }
                print(f"🎯 成功獲取 API 數據: {payload}")
                
                res = requests.post(API_URL, data=json.dumps(payload), timeout=20)
                print(f"📡 試算表回應: {res.text}")
            else:
                print("❌ 無法在數據流中定位銷量格式。可能是網頁關閉或結構大幅更動。")
        else:
            print("❌ 目標伺服器目前無法連線。")

    except Exception as e:
        print(f"⚠️ 異常中斷: {e}")

if __name__ == "__main__":
    run()
