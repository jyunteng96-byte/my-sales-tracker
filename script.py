import requests
import json
import re

# 這是你剛提供的新 URL
API_URL = "https://script.google.com/macros/s/AKfycbzxlhIKNZJmOiL5if0LSNGe5rhZgwP3BSRUEDbIjD-psi7qTJBT-BWXC5rC1jqF5y3WPg/exec"
TARGET_URL = "https://kay-s-cut-0411yuna.streamlit.app/"

def run():
    print("🚀 啟動強化匹配模式...")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    }

    try:
        response = requests.get(TARGET_URL, headers=headers, timeout=30)
        content = response.text
        
        # 搜尋 Unicode 編碼或純文字的「總銷量」數字
        match = re.search(r"\\u7e3d\\u92b7\\u91cf.*?(\d+)", content) or re.search(r"總銷量[:：]\s*(\d+)", content)
        # 搜尋時間 [HH:mm:ss]
        time_match = re.search(r"(\d{2}:\d{2}:\d{2})", content)

        if match:
            total_sales = match.group(1)
            time_val = time_match.group(1) if time_match else "00:00:00"
            
            payload = {
                "time": time_val,
                "totalSales": total_sales,
                "diff": "0", # 差值會由試算表自動計算
                "stock": 8000 - int(total_sales)
            }
            
            print(f"🎯 成功擷取！銷量：{total_sales}，時間：{time_val}")
            res = requests.post(API_URL, data=json.dumps(payload), timeout=20)
            print(f"📡 試算表回應: {res.text}")
        else:
            print("❌ 數據定位失敗，可能是網頁內容尚未加載或格式改變。")

    except Exception as e:
        print(f"⚠️ 執行錯誤: {e}")

if __name__ == "__main__":
    run()
