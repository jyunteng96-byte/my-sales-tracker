import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 1. 網頁基本設定
st.set_page_config(page_title="實時cut監控", layout="wide")

st.title("📊 ALLDAY PROJECT 實時數據看板")

# 2. 建立連線 (請換成你的試算表網址)
# 確保試算表已開啟「知道連結的人皆可檢視」
SHEET_URL = "https://docs.google.com/spreadsheets/d/1cVlCR18b9wzYBwBswPB3E9A_sy4nNZ2BVAkF4Db5g_c/edit?usp=sharing"

try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    # 讀取數據，不設定 ttl 代表每次刷新都抓最新的
    df = conn.read(spreadsheet=SHEET_URL, ttl=0)
    
    # 確保數據不是空的
    if not df.empty:
        # 3. 頂部大數字區
        last_data = df.iloc[-1]  # 最新一筆
        
        # 建立三個漂亮的區塊
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(label="🔥 當前總銷量", value=int(last_data['總銷量']), delta=int(last_data['差值']))
        with col2:
            st.metric(label="📦 剩餘總庫存", value=int(last_data['總庫存']))
        with col3:
            st.metric(label="🕒 最後更新", value=str(last_data['時刻']).split(" ")[-1])

        st.divider()

        # 4. 數據清單區
        st.subheader("📋 歷史詳細紀錄")
        
        # 將最新的紀錄排在最上面，並隱藏最左邊的索引號
        st.dataframe(
            df.sort_values(by='時刻', ascending=False), 
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("目前試算表內尚無數據紀錄。")

except Exception as e:
    st.error(f"連線失敗！請確認試算表網址是否正確。錯誤訊息: {e}")

# 5. 自動重新整理提示
st.caption("提示：手動重新整理網頁即可獲取最新數據。")