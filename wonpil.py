import streamlit as st
import pandas as pd
import urllib.parse
import time

# --- 配置區 ---
SHEET_ID = "11UXviXGiGJ33aRss2TdIL5b57vp8jrvqvjclK-TPkY8"
SHEET_NAME = "工作表1"

def get_data():
    # 加入隨機參數防止快取舊資料
    encoded_sheet_name = urllib.parse.quote(SHEET_NAME)
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={encoded_sheet_name}&t={int(time.time())}"
    
    # 讀取 CSV
    df = pd.read_csv(url)
    
    # 鎖定前三欄並重新命名
    df = df.iloc[:, :3]
    df.columns = ['時刻', '總銷量', '變化量']
    
    # 處理時間格式，修正下午/上午字眼
    df['時刻'] = df['時刻'].astype(str).str.replace('下午', ' PM').str.replace('上午', ' AM')
    df['時刻'] = pd.to_datetime(df['時刻'], errors='coerce')
    
    # 移除無法辨識日期的行 (例如標題或測試數據)
    df = df.dropna(subset=['時刻'])
    
    # 清洗數字數據
    df['變化量'] = pd.to_numeric(df['變化量'].astype(str).str.replace('+', '', regex=False).replace('紀錄更新', '0'), errors='coerce').fillna(0)
    df['總銷量'] = pd.to_numeric(df['總銷量'], errors='coerce').fillna(0)
    
    # 【關鍵過濾】只顯示「今天之後」的資料，徹底解決 3 月舊數據問題
    # 使用 2026/04/01 作為門檻值
    threshold_date = pd.Timestamp('2026-04-01')
    df = df[df['時刻'] >= threshold_date]
    
    return df.sort_values('時刻')

st.set_page_config(page_title="購買量排行", page_icon="📊", layout="wide")
st.title("📊 購買量排行")

try:
    df = get_data()
    
    if not df.empty:
        latest = df.iloc[-1]
        c1, c2 = st.columns(2)
        # 顯示最新正確總額
        c1.metric("目前累積總量", f"{int(latest['總銷量'])} 張")
        c2.metric("最後更新時間", latest['時刻'].strftime('%Y/%m/%d %H:%M:%S'))

        st.markdown("---")

        # 購買量排行：僅顯示有增加且日期正確的紀錄
        all_rank = df[df['變化量'] > 0].sort_values('變化量', ascending=False).copy()
        
        if not all_rank.empty:
            all_rank['交易時刻'] = all_rank['時刻'].dt.strftime('%m/%d %H:%M:%S')
            display_df = all_rank[['交易時刻', '總銷量', '變化量']].reset_index(drop=True)
            display_df.columns = ['交易時刻', '當時累積總量', '單次購買量']
            display_df.index += 1
            
            st.dataframe(display_df, use_container_width=True, height=600)
        else:
            st.info("4 月份目前尚無偵測到購買紀錄。")
            
    else:
        st.warning("⚠️ 未偵測到 4 月份的有效數據。請確認試算表日期是否正確。")

except Exception as e:
    st.error("解析異常")
    st.write(f"系統訊息：{e}")

if st.sidebar.button("手動刷新數據"):
    st.rerun()
