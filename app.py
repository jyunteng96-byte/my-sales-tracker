import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 1. 網頁基本設定
st.set_page_config(page_title="實時cut數據", layout="wide")

st.title("ALLDAY PROJECT 排名")

# 2. 建立連線
SHEET_URL = "https://docs.google.com/spreadsheets/d/1cVlCR18b9wzYBwBswPB3E9A_sy4nNZ2BVAkF4Db5g_c/edit?usp=sharing"

try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    # ttl=0 確保每次重新整理都抓最新
    df = conn.read(spreadsheet=SHEET_URL, ttl=0)
    
    if not df.empty:
        # --- 前半段：大數字看板 (保留你原本喜歡的內容) ---
        last_data = df.iloc[-1]
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(label="當前總銷量", value=int(last_data['總銷量']), delta=int(last_data['差值']))
        with col2:
            st.metric(label="剩餘總庫存", value=int(last_data['總庫存']))
        with col3:
            st.metric(label="最後更新", value=str(last_data['時刻']).split(" ")[-1])

        st.divider()

        # --- 後半段：進階排名表 (新功能) ---
        st.subheader("近期銷量變動排名")
        
        # 這裡假設你的表裡有「項目名稱」或「成員」欄位
        # 如果你只想看「最近幾次更新」的差值排序：
        recent_df = df.tail(10).copy() # 抓最後 10 筆紀錄
        
        # 依照「差值」從大到小排序
        ranked_df = recent_df.sort_values(by='差值', ascending=False)
        
        # 裝飾一下表格：加上排名序號
        ranked_df.insert(0, '排名', range(1, len(ranked_df) + 1))

        # 顯示表格，並對「差值」欄位加上顏色高亮
        st.dataframe(
            ranked_df[['排名', '時刻', '總銷量', '差值']], 
            use_container_width=True,
            hide_index=True,
            column_config={
                "差值": st.column_config.NumberColumn(
                    "增長量",
                    help="與上一分鐘相比的銷量變化",
                    format="+%d"
                )
            }
        )
        
    else:
        st.info("尚無數據。")

except Exception as e:
    st.error(f"連線失敗: {e}")
