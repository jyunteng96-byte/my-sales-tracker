import requests
import json
import re

# 請確認 Apps Script 網址正確
API_URL = "https://script.google.com/macros/s/AKfycbyVJt9fT7WBSbY0AOV07mluUv1bO2GJZ0usyfjtZClvaaSwfOSI3c-Qzn9a9uIYCmhNWQ/exec"
TARGET_URL = "https://kay-s-cut-0411yuna.streamlit.app/"

def run():
    print("🚀 啟動模糊匹配抓取模式...")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7'
    }

    try:
        response = requests.get(TARGET_URL, headers=headers, timeout=30)
        content = response.text
        
        # 1. 抓取「總銷量」後面的數字
        total_sales_match = re.search(r"總銷量[:：]\s*(\d+)", content)
        # 2. 抓取「+」或「-」開頭的變動數字
        diff_match = re.search(r"([+-]\d+)", content)
        # 3. 抓取時間格式 (HH:mm:ss)
        time_match = re.search(r"(\d{2}:\d{2}:\d{2})", content)

        if total_sales_match and time_match:
            total_sales = total_sales_match.group(1)
            time_val = time_match.group(1)
            # 如果抓不到變動值，預設為 0
            diff_val = diff_match.group(1).replace("+", "") if diff_match else "0"
            
            payload = {
                "time": time_val,
                "totalSales": total_sales,
                "diff": diff_val,
                "stock": 8000 - int(total_sales)
            }
            
            print(f"🎯 成功匹配！時間: {time_val}, 總銷量: {total_sales}")
            
            res = requests.post(API_URL, data=json.dumps(payload), timeout=20)
            print(f"📡 試算表回應: {res.text}")
        else:
            print("❌ 模糊匹配失敗。")
            # 幫助偵錯：印出是否有抓到任何關鍵字
            print(f"偵測結果：總銷量={bool(total_sales_match)}, 時間={bool(time_match)}")

    except Exception as e:
        print(f"⚠️ 異常: {e}")

if __name__ == "__main__":
    run()
