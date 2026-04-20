import streamlit as st
import pandas as pd
import urllib.parse
import time

# --- 配置區 ---
SHEET_ID = "11UXviXGiGJ33aRss2TdIL5b57vp8jrvqvjclK-TPkY8"
SHEET_NAME = "工作表1"

def get_data():
    # 強制禁用 Google 快取
    encoded_sheet_name = urllib.parse.quote(SHEET_NAME)
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={encoded_sheet_name}&t={int(time.time())}"
    
    # 讀取 CSV
    df = pd.read_csv(url)
    
    # 強制鎖定前三欄：時刻、總銷量、變化量
    df = df.iloc[:, :3]
    df.columns = ['時刻', '總銷量', '變化量']
    
    # 處理時間格式 (上午/下午)
    df['時刻'] = df['時刻'].astype(str).str.replace('下午', ' PM').str.replace('上午', ' AM')
    df['時刻'] = pd.to_datetime(df['時刻'], errors='coerce')
    
    # 清洗數字數據
    df['變化量'] = pd.to_numeric(df['變化量'].astype(str).str.replace('+', '', regex=False).replace('紀錄更新', '0'), errors='coerce').fillna(0)
    df['總銷量'] = pd.to_numeric(df['總銷量'], errors='coerce').fillna(0)
    
    # 只刪除解析日期完全失敗的空行
    return df.dropna(subset=['時刻']).sort_values('時刻', ascending=False)

st.set_page_config(page_title="購買量排行", page_icon="📊", layout="wide")
st.title("📊 購買量排行")

try:
    df = get_data()
    
    if not df.empty:
        # 指標區 (顯示最新的一筆)
        latest = df.iloc[0]
        c1, c2 = st.columns(2)
        c1.metric("目前累積總量", f"{int(latest['總銷量'])} 張")
        c2.metric("最後更新時間", latest['時刻'].strftime('%Y/%m/%d %H:%M:%S'))

        st.markdown("---")

        # 側邊欄過濾功能：您可以決定要不要看三月份或異常大的數據
        st.sidebar.header("數據篩選")
        min_qty = st.sidebar.number_input("顯示單次購買大於：", value=1)
        max_qty = st.sidebar.number_input("隱藏單次購買大於：", value=5000)
        show_all_dates = st.sidebar.checkbox("顯示所有月份數據 (包含 3 月)", value=True)

        # 執行過濾邏輯
        filtered_df = df[df['變化量'] >= min_qty]
        filtered_df = filtered_df[filtered_df['變化量'] <= max_qty]
        
        if not show_all_dates:
            # 如果不勾選，則只看 4 月份
            filtered_df = filtered_df[filtered_df['時刻'] >= pd.Timestamp('2026-04-01')]

        # --- 顯示排行榜 ---
        if not filtered_df.empty:
            # 按單次購買量降序排列
            rank_df = filtered_df.sort_values('變化量', ascending=False).copy()
            rank_df['交易時刻'] = rank_df['時刻'].dt.strftime('%m/%d %H:%M:%S')
            
            display_df = rank_df[['交易時刻', '總銷量', '變化量']].reset_index(drop=True)
            display_df.columns = ['交易時刻', '累積總銷量', '單次購買量']
            display_df.index += 1
            
            # 使用 st.table 直接展開所有數據
            st.table(display_df)
        else:
            st.warning("當前篩選條件下無數據，請調整左側篩選器。")
            
    else:
        st.error("試算表內目前是空的，或讀取失敗。")

except Exception as e:
    st.error(f"解析崩潰：{e}")

if st.sidebar.button("手動強制重新抓取"):
    st.rerun()
