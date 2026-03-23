import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 網頁設定
st.set_page_config(page_title="YUNA台北簽售實時cut", layout="centered")

# 1. 連線到 Google Sheets
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    # ttl=0 確保即時抓取最新試算表數據
    df = conn.read(ttl=0)
except Exception as e:
    st.error("連線失敗，請檢查 Secrets 中的 spreadsheet 網址是否正確。")
    st.stop()

if not df.empty:
    # 2. 數值格式轉換
    cols_to_fix = ['總庫存', '總銷量', '差值(本次購買)']
    for col in cols_to_fix:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # 3. 核心邏輯：抵銷退單 (相反數完全抵銷)
    valid_indices = list(df.index)
    # 尋找負數（退單）
    for i in df[df['差值(本次購買)'] < 0].index:
        refund_val = abs(df.loc[i, '差值(本次購買)'])
        # 在這筆退單之前，尋找是否有相同數值的購買紀錄
        match = df[(df.index < i) & 
                   (df['差值(本次購買)'] == refund_val) & 
                   (col in df.columns) &
                   (df.index.isin(valid_indices))].last_valid_index()
        if match is not None:
            valid_indices.remove(i)      # 移除退單
            valid_indices.remove(match)  # 移除原購買單

    # 取得抵銷後的乾淨資料
    clean_df = df.loc[valid_indices].copy()

    # --- A. 上方看板 ---
    st.title("📊 TDK 銷售實時全榜單")
    latest = df.iloc[-1]
    
    c1, c2, c3 = st.columns(3)
    c1.metric("剩餘庫存", f"{int(latest['總庫存'])}")
    c2.metric("累計銷量", f"{int(latest['總銷量'])}")
    c3.metric("最近更新", str(latest['時刻']).split(".")[0])

    st.divider()

    # --- B. 全體排行榜 (移除數量限制) ---
    st.subheader("每筆購買量排行")
    
    # 篩選掉 0 與 負數，按「差值」由大到小進行全體排序
    # 💡 這裡拿掉了 .head(15)，會顯示所有資料
    rank_df = clean_df[clean_df['差值(本次購買)'] > 0].sort_values(by='差值(本次購買)', ascending=False).copy()
    
    if not rank_df.empty:
        # 重設索引為排名 1, 2, 3...
        rank_df = rank_df.reset_index(drop=True)
        rank_df.index = rank_df.index + 1
        rank_df.index.name = "排名"

        # 整理顯示欄位
        final_table = rank_df[['時刻', '差值(本次購買)']]
        final_table.columns = ['成交時間', '購買數量']
        
        # 顯示完整表格
        st.table(final_table)
    else:
        st.info("目前尚無有效成交紀錄。")

else:
    st.warning("試算表目前是空的，請確認 GAS 程式已執行。")
