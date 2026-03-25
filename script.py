import json
import requests
import re
from playwright.sync_api import sync_playwright

# 這是你最新的 URL
API_URL = "https://script.google.com/macros/s/AKfycbzxlhIKNZJmOiL5if0LSNGe5rhZgwP3BSRUEDbIjD-psi7qTJBT-BWXC5rC1jqF5y3WPg/exec"
TARGET_URL = "https://kay-s-cut-0411yuna.streamlit.app/"

def run():
    with sync_playwright() as p:
        print("🚀 啟動雲端模擬瀏覽器...")
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        try:
            page.goto(TARGET_URL, wait_until="networkidle")
            print("⏳ 正在等待數據渲染 (預計 30 秒)...")
            
            # 這是關鍵：讓腳本反覆檢查畫面內容，直到出現「總銷量」
            found = False
            for _ in range(10): # 最多檢查 10 次
                content = page.content()
                # 使用廣義匹配：找到包含「總銷量」文字及其後的數字
                match = re.search(r"總銷量[:：]\s*(\d+)", content)
                time_match = re.search(r"(\d{2}:\d{2}:\d{2})", content)
                
                if match:
                    total_sales = match.group(1)
                    time_val = time_match.group(1) if time_match else "00:00:00"
                    
                    payload = {
                        "time": time_val,
                        "totalSales": total_sales,
                        "diff": "0",
                        "stock": 8000 - int(total_sales)
                    }
                    
                    print(f"🎯 成功鎖定數據！銷量：{total_sales}")
                    res = requests.post(API_URL, data=json.dumps(payload), timeout=20)
                    print(f"📡 試算表回應: {res.text}")
                    found = True
                    break
                else:
                    print("...數據加載中，稍候 5 秒...")
                    page.wait_for_timeout(5000)

            if not found:
                print("❌ 最終失敗：網頁仍未顯示數據。")

        except Exception as e:
            print(f"⚠️ 執行異常: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    run()
