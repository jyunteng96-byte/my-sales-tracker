import streamlit as st
import pandas as pd
import urllib.parse
import time

# --- 基礎配置 ---
SHEET_ID = "11UXviXGiGJ33aRss2TdIL5b57vp8jrvqvjclK-TPkY8"
SHEET_NAME = "工作表1"

def get_data():
    # 強制禁用快取，確保讀到最新數據
    encoded_sheet_name = urllib.parse.quote(SHEET_NAME)
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={encoded_sheet_name}&t={int(time.time())}"
    
    # 讀取 CSV
    df = pd.read_csv(url)
    
    # 照抄前三欄：時刻、總銷量、變化量
    df = df.iloc[:, :3]
    df.columns = ['時刻', '總銷量', '變化量']
    
    # 清理數字格式，確保可以排序
    df['變化量'] = pd.to_numeric(df['變化量'].astype(str).str.replace('+', '', regex=False), errors='coerce').fillna(0)
    df['總銷量'] = pd.to_numeric(df['總銷量'], errors='coerce').fillna(0)
    
    # 移除空行
    return df.dropna(subset=['時刻'])

st.set_page_config(page_title="購買量排行", layout="wide")
st.title("📊 購買量排行")

try:
    df = get_data()
    
    if not df.empty:
        # 指標區：顯示目前最新的一筆紀錄
        latest = df.iloc[-1]
        c1, c2 = st.columns(2)
        c1.metric("目前累積總量", f"{int(latest['總銷量'])} 張")
        c2.metric("最後更新時間", str(latest['時刻']))

        st.markdown("---")

        # --- 購買量排行：表上寫什麼就抄什麼，僅按變化量排序 ---
        # 只要變化量大於 0 的全部顯示
        rank_df = df[df['變化量'] > 0].sort_values('變化量', ascending=False).copy()
        
        if not rank_df.empty:
            # 整理顯示欄位名
            display_df = rank_df[['時刻', '總銷量', '變化量']].reset_index(drop=True)
            display_df.columns = ['交易時刻', '累積總銷量', '單次購買量']
            display_df.index += 1 # 排名從 1 開始
            
            # 直接展開全部數據表格
            st.table(display_df)
        else:
            st.write("目前沒有偵測到購買紀錄。")
            
    else:
        st.error("讀取失敗，請確認試算表權限。")

except Exception as e:
    st.error(f"系統錯誤：{e}")

# 側邊欄重新整理
if st.sidebar.button("立即刷新"):
    st.rerun()
