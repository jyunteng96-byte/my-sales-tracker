import streamlit as st
import pandas as pd
import urllib.parse
import time

# --- 配置區 ---
SHEET_ID = "11UXviXGiGJ33aRss2TdIL5b57vp8jrvqvjclK-TPkY8"
SHEET_NAME = "工作表1"

def get_data():
    # 加上隨機參數強制 Google 刷新，避免抓到三月的舊快取
    encoded_sheet_name = urllib.parse.quote(SHEET_NAME)
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={encoded_sheet_name}&t={int(time.time())}"
    
    # 直接讀取全部 CSV
    df = pd.read_csv(url)
    
    # 1. 暴力鎖定前三欄：時刻、總銷量、變化量
    df = df.iloc[:, :3]
    df.columns = ['時刻', '總銷量', '變化量']
    
    # 2. 清洗數字 (只刪除非數字的東西，保留所有表上的內容)
    df['變化量'] = pd.to_numeric(df['變化量'].astype(str).str.replace('+', '', regex=False), errors='coerce').fillna(0)
    df['總銷量'] = pd.to_numeric(df['總銷量'], errors='coerce').fillna(0)
    
    # 3. 移除完全空白的行
    df = df.dropna(subset=['時刻'])
    
    return df

st.set_page_config(page_title="購買量排行", layout="wide")
st.title("📊 購買量排行")

try:
    df = get_data()
    
    if not df.empty:
        # 【關鍵修正】直接抓取試算表最後一行，那才是您現在最新的 40 幾筆數據
        latest = df.iloc[-1]
        
        c1, c2 = st.columns(2)
        # 直接呈現表上的文字，不再做日期轉換，避免 4/20 變 3/25
        c1.metric("目前累積總量", f"{int(latest['總銷量'])} 張")
        c2.metric("最後更新時刻", str(latest['時刻']))

        st.markdown("---")

        # --- 購買量排行：表上寫什麼就抄什麼 ---
        # 只要變化量 > 0，按大小排序
        rank_df = df[df['變化量'] > 0].sort_values('變化量', ascending=False).copy()
        
        if not rank_df.empty:
            display_df = rank_df[['時刻', '總銷量', '變化量']].reset_index(drop=True)
            display_df.columns = ['交易時刻', '累積總量', '單次購買']
            display_df.index += 1
            
            # 使用 table 確保全部展開
            st.table(display_df)
        else:
            st.write("目前沒有偵測到任何單次購買量 > 0 的紀錄。")
            
    else:
        st.error("試算表讀取為空，請確認內容。")

except Exception as e:
    st.error(f"連線失敗：{e}")

if st.sidebar.button("強制刷新"):
    st.rerun()
