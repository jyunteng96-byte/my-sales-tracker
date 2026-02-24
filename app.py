import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 1. 網頁基本設定
st.set_page_config(page_title="ALLDAY PROJECT 實時cut數據", layout="wide")

st.title("ALLDAY PROJECT 實時cut數據")
st.markdown("---")

# 2. 建立連線 (請確認你的試算表已開啟「知道連結的人皆可檢視」)
SHEET_URL = "https://docs.google.com/spreadsheets/d/1cVlCR18b9wzYBwBswPB3E9A_sy4nNZ2BVAkF4Db5g_c/edit?usp=sharing" # 請確認此處為你的網址

try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    # ttl=0 確保每次刷新都抓取最新數據
    df = conn.read(spreadsheet=SHEET_URL, ttl=0)
    
    if not df.empty:
        # --- A. 頂部看板 (顯示最新一筆狀態) ---
        last_data = df.iloc[-1]
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(label="當前總銷量", value=int(last_data['總銷量']), delta=int(last_data['差值']))
        with col2:
            st.metric(label="剩餘總庫存", value=int(last_data['總庫存']))
        with col3:
            st.metric(label="最後更新時間", value=str(last_data['時刻']).split(" ")[-1])

        st.divider()

        # --- B. 進階排名邏輯 ---
        st.subheader("銷量增長排名 (已過濾買退抵銷)")

        # 1. 複製原始數據進行處理
        rank_df = df.copy()

        # 2. 過濾邏輯：如果當前差值與上一筆或下一筆互為相反數，則視為「買了又退」，將其剔除
        if len(rank_df) > 1:
            # 標記需要刪除的行 (當前值 == -下一筆值 OR 當前值 == -前一筆值)
            mask_drop = (rank_df['差值'] == -rank_df['差值'].shift(-1)) | (rank_df['差值'] == -rank_df['差值'].shift(1))
            rank_df = rank_df[~mask_drop]

        # 3. 排序：依照差值 (增長量) 從大到小排列所有數據
        ranked_df = rank_df.sort_values(by='差值', ascending=False)

        # 4. 欄位精簡：移除總銷量、總庫存，僅保留時刻與差值
        display_df = ranked_df[['時刻', '差值']].copy()

        # 5. 加入排名序號
        display_df.insert(0, '排名', range(1, len(display_df) + 1))

        # 6. 顯示優化後的表格
        st.dataframe(
            display_df, 
            use_container_width=True,
            hide_index=True,
            column_config={
                "時刻": st.column_config.DatetimeColumn("更新時間", format="YYYY/MM/DD HH:mm:ss"),
                "差值": st.column_config.NumberColumn(
                    "增長量",
                    help="排除抵銷後的實際變動",
                    format="+%d"
                )
            }
        )
        
    else:
        st.info("目前試算表內尚無數據。")

except Exception as e:
    st.error(f"數據讀取失敗，請檢查試算表網址與權限。錯誤: {e}")

# 底部提示
st.caption("提示：數據每分鐘隨 GAS 自動更新，手動重新整理網頁可獲取最新排名。")


