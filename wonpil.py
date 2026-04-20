import streamlit as st
import pandas as pd
import urllib.parse
import time

# --- 配置區 ---
SHEET_ID = "11UXviXGiGJ33aRss2TdIL5b57vp8jrvqvjclK-TPkY8"
SHEET_NAME = "工作表1"

def get_data():
    # 強制跳過快取
    encoded_sheet_name = urllib.parse.quote(SHEET_NAME)
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={encoded_sheet_name}&t={int(time.time())}"
    
    # 直接讀取
    df = pd.read_csv(url)
    
    # 暴力命名：不管原本叫什麼，前三欄就是這三個名字
    df.columns = ['時刻', '總銷量', '變化量'] + list(df.columns[3:])
    
    # 處理時間：把中文上午/下午轉掉
    df['時刻'] = df['時刻'].astype(str).str.replace('下午', ' PM').str.replace('上午', ' AM')
    df['時刻'] = pd.to_datetime(df['時刻'], errors='coerce')
    
    # 清洗數字
    df['變化量'] = pd.to_numeric(df['變化量'].astype(str).str.replace('+', '', regex=False).replace('紀錄更新', '0'), errors='coerce').fillna(0)
    df['總銷量'] = pd.to_numeric(df['總銷量'], errors='coerce').fillna(0)
    
    # 拿掉所有日期過濾，只刪除解析失敗的廢行
    df = df.dropna(subset=['時刻'])
    
    return df.sort_values('時刻')

st.set_page_config(page_title="購買量排行", page_icon="📊", layout="wide")

st.title("📊 購買量排行")

try:
    df = get_data()
    
    if not df.empty:
        # 指標顯示最後一筆
        latest = df.iloc[-1]
        c1, c2 = st.columns(2)
        c1.metric("目前累積總量", f"{int(latest['總銷量'])} 張")
        c2.metric("最後更新時間", latest['時刻'].strftime('%Y/%m/%d %H:%M:%S'))

        st.markdown("---")

        # 排行榜：只要變化量 > 0 且不等於異常大數字的全部列出
        all_rank = df[(df['變化量'] > 0) & (df['變化量'] < 5000)].sort_values('變化量', ascending=False).copy()
        
        if not all_rank.empty:
            all_rank['交易時刻'] = all_rank['時刻'].dt.strftime('%m/%d %H:%M:%S')
            display_df = all_rank[['交易時刻', '總銷量', '變化量']].reset_index(drop=True)
            display_df.columns = ['交易時刻', '當時累積總量', '單次購買量']
            display_df.index += 1
            
            # 使用靜態表格 st.table 確保 40 筆數據能直接全部展開
            st.table(display_df)
        else:
            st.write("目前試算表中沒有購買量大於 0 的紀錄。")
            
    else:
        st.write("讀取不到數據，請檢查試算表。")

except Exception as e:
    st.error(f"解析發生錯誤：{e}")

st.sidebar.button("手動刷新")
