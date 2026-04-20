import streamlit as st
import pandas as pd
import urllib.parse
import time

# --- 【關鍵修正】使用您提供的正確試算表 ID ---
SHEET_ID = "1LT9LH5M9q7fx7Or_ZvYIeQEcndjyfOKqqDlC-kMMz9k"
SHEET_NAME = "工作表1"

def get_data():
    # 強制禁用快取，確保同步抓取最新數據
    encoded_sheet_name = urllib.parse.quote(SHEET_NAME)
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={encoded_sheet_name}&t={int(time.time())}"
    
    # 1. 直接讀取 CSV，不做任何日期解析，避免 4月變3月
    df = pd.read_csv(url)
    
    # 2. 鎖定前三欄：時刻、總銷量、變化量
    df = df.iloc[:, :3]
    df.columns = ['時刻', '總銷量', '變化量']
    
    # 3. 唯獨將數字欄位轉為數字，以便進行排序
    df['變化量'] = pd.to_numeric(df['變化量'].astype(str).str.replace('+', '', regex=False), errors='coerce').fillna(0)
    df['總銷量'] = pd.to_numeric(df['總銷量'], errors='coerce').fillna(0)
    
    # 4. 移除時刻為空的行
    return df.dropna(subset=['時刻'])

st.set_page_config(page_title="購買量排行", layout="wide")
st.title("📊 購買量排行")

try:
    df = get_data()
    
    if not df.empty:
        # 指標區：直接顯示試算表「最後一行」的最新數據
        latest = df.iloc[-1]
        
        c1, c2 = st.columns(2)
        c1.metric("目前累積總量", f"{int(latest['總銷量'])} 張")
        c2.metric("最後更新時刻", str(latest['時刻']))

        st.markdown("---")

        # --- 購買量排行：表上寫什麼就抄什麼，僅按變化量排序 ---
        # 只要變化量 > 0 的紀錄全部列出
        rank_df = df[df['變化量'] > 0].sort_values('變化量', ascending=False).copy()
        
        if not rank_df.empty:
            display_df = rank_df[['時刻', '總銷量', '變化量']].reset_index(drop=True)
            display_df.columns = ['交易時刻', '累積總量', '單次購買']
            display_df.index += 1 # 排名序號
            
            # 使用 table 直接完整展開數據
            st.table(display_df)
        else:
            st.write("目前尚未偵測到單次購買量紀錄。")
            
    else:
        st.error("讀取不到數據，請確認試算表分頁名稱是否為「工作表1」。")

except Exception as e:
    st.error(f"連線或解析失敗：{e}")

if st.sidebar.button("強制刷新數據"):
    st.rerun()
