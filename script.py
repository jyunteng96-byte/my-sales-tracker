import websocket
import json
import re
import requests

# 你的 Google Apps Script 網址
API_URL = "https://script.google.com/macros/s/AKfycbzxlhIKNZJmOiL5if0LSNGe5rhZgwP3BSRUEDbIjD-psi7qTJBT-BWXC5rC1jqF5y3WPg/exec"
WS_URL = "wss://kay-s-cut-0411yuna.streamlit.app/_stcore/stream"

def on_message(ws, message):
    # Streamlit 的數據通常是二進位或混淆文字，我們直接在原始封包找數字
    content = str(message)
    
    # 搜尋格式：[16:04:01] +20 (總銷量: 2676)
    # 或是 Unicode 轉義後的格式
    pattern = r"(\d{2}:\d{2}:\d{2}).*?([+-]\d+).*?(\d+)"
    match = re.search(pattern, content)
    
    if match:
        time_val = match.group(1)
        diff = match.group(2).replace("+", "")
        total_sales = match.group(3)
        
        payload = {
            "time": time_val,
            "totalSales": total_sales,
            "diff": diff,
            "stock": 8000 - int(total_sales)
        }
        
        print(f"🎯 WebSocket 攔截成功: {payload}")
        res = requests.post(API_URL, data=json.dumps(payload), timeout=15)
        print(f"📡 試算表回應: {res.text}")
        ws.close() # 抓到就關閉

def run():
    print("🚀 正在建立 WebSocket 連線...")
    ws = websocket.WebSocketApp(WS_URL,
                              on_message=on_message,
                              header={"User-Agent": "Mozilla/5.0"})
    # 設定超時，避免無限等待
    ws.run_forever(timeout=30)

if __name__ == "__main__":
    run()
