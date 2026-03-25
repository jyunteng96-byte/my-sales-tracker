import requests
import json
import time

# 你的 Google Apps Script 網址
API_URL = "https://script.google.com/macros/s/AKfycbyVJt9fT7WBSbY0AOV07mluUv1bO2GJZ0usyfjtZClvaaSwfOSI3c-Qzn9a9uIYCmhNWQ/exec"
# 目標網頁資料接口 (Streamlit 的狀態通常藏在渲染後的內容)
TARGET_URL = "https://kay-s-cut-0411yuna.streamlit.app/"

def run():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,/ ;q=0.8'
    }
    
    try:
        # 第一步：嘗試獲取網頁快照
        response = requests.get(TARGET_URL, headers=headers, timeout=30)
        content = response.text
        
        # 使用更強大的搜索機制：找尋包含 "總銷量" 的文字塊
        # 這種寫法能應對 Streamlit 稍微變動的標籤
        import re
        # 找尋類似 [16:04:01] +20 (總銷量: 2676) 的內容
        pattern = r"\[(\d{2}:\d{2}:\d{2})\]\s*([+-]\d+)\s*\(總銷量:\s*(\d+)\)"
        matches = re.findall(pattern, content)

        if matches:
            # 取最後一筆 (最新的一筆)
            latest = matches[0]
            payload = {
                "time": latest[0],
                "diff": latest[1].replace("+", ""),
                "totalSales": latest[2],
                "stock": 8000 - int(latest[2])
            }
            
            # 傳送到你的 Google 試算表
            res = requests.post(API_URL, data=json.dumps(payload))
            print(f"✅ 成功抓取！數據時間: {latest[0]}, 銷量: {latest[2]}, 回應: {res.text}")
        else:
            # 如果還是抓不到，印出網頁前 1000 個字元來分析原因
            print("❌ 依然抓不到格式。這代表雲端伺服器被 Streamlit 的加載畫面擋住了。")
            print("DEBUG 資訊 (網頁片段):", content[:1000])

    except Exception as e:
        print(f"⚠️ 執行發生錯誤: {e}")

if __name__ == "__main__":
    run()
