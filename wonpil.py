import streamlit as st
import pandas as pd
import urllib.parse
import time

# --- 最基礎配置 ---
SHEET_ID = "11UXviXGiGJ33aRss2TdIL5b57vp8jrvqvjclK-TPkY8"
SHEET_NAME = "工作表1"

def get_data():
    # 強制禁用 Google 快取
    encoded_sheet_name = urllib.parse.quote(SHEET_NAME)
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={encoded_sheet_name}&t={int(time.time())}"
    
    # 1. 直接讀取 CSV，不做任何日期處理 (parse_dates=False)
    df = pd.read_csv(url)
    
    # 2. 暴力鎖定前三欄：時刻、總銷量、變化量
    df = df.iloc[:, :3]
    df.columns = ['時刻', '總銷量', '變化量']
    
    # 3. 唯獨把「數字欄位」轉成數字，以便排序
    # 移除符號，轉換失敗的填 0
    df['變化量'] = pd.to_numeric(df['變化量'].astype(str).str.replace('+', '', regex=False), errors='coerce').fillna(0)
    df['總銷量'] = pd.to_numeric(df['總銷量'], errors='coerce').fillna(0)
    
    # 4. 刪除完全沒資料的空行
    df = df.dropna(subset=['時刻'])
    
    return df

st.set_page_config(page_title="購買量排行", layout="wide")
st.title("📊 購買量排行")

try:
    df = get_data()
    
    if not df.empty:
        # 指標區：直接抓試算表的最後一行 (保證是最新那筆)
        latest = df.iloc[-1]
        
        c1, c2 = st.columns(2)
        c1.metric("目前累積總量", f"{int(latest['總銷量'])} 張")
        c2.metric("最後更新時刻", str(latest['時刻'])) # 直接顯示原始文字

        st.markdown("---")

        # --- 購買量排行：表上寫什麼就抄什麼 ---
        # 只要變化量 > 0，按大小排序
        rank_df = df[df['變化量'] > 0].sort_values('變化量', ascending=False).copy()
        
        if not rank_df.empty:
            # 重新整理顯示用的 DataFrame
            display_df = rank_df[['時刻', '總銷量', '變化量']].reset_index(drop=True)
            display_df.columns = ['交易時刻', '累積總量', '單次購買']
            display_df.index += 1
            
            # 使用 st.table 直接顯示全部 40 幾筆
            st.table(display_df)
        else:
            st.write("目前沒有偵測到單次購買量 > 0 的紀錄。")
            
    else:
        st.error("試算表讀取為空。")

except Exception as e:
    st.error(f"連線失敗：{e}")

if st.sidebar.button("強制刷新"):
    st.rerun()
