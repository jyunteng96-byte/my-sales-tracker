import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 網頁基本設定
st.set_page_config(page_title="K-MONSTAR實時cut", layout="centered")

# 1. 建立連線
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(ttl=0)
except Exception as e:
    st.error("連線失敗，請檢查 Secrets 設定。")
    st.stop()

if not df.empty:
    # 數值轉換
    numeric_cols = ['台灣差值', '國外差值', '每筆銷量(本次)', '總銷量(累積)']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # --- 核心邏輯：抵銷退單 ---
    valid_indices = list(df.index)
    for i in df[df['台灣差值'] < 0].index:
        val = abs(df.loc[i, '台灣差值'])
        match = df[(df.index < i) & (df['台灣差值'] == val) & (df.index.isin(valid_indices))].last_valid_index()
        if match is not None:
            valid_indices.remove(i); valid_indices.remove(match)
    for i in df[df['國外差值'] < 0].index:
        val = abs(df.loc[i, '國外差值'])
        match = df[(df.index < i) & (df['國外差值'] == val) & (df.index.isin(valid_indices))].last_valid_index()
        if match is not None:
            if i in valid_indices: valid_indices.remove(i)
            if match in valid_indices: valid_indices.remove(match)

    clean_df = df.loc[valid_indices].copy()

    # --- 站點標註邏輯 ---
    def get_source(row):
        if row['台灣差值'] > 0 and row['國外差值'] > 0: return "雙站合計"
        elif row['台灣差值'] > 0: return "台灣站"
        elif row['國外差值'] > 0: return "國際站"
        return "無變動"

    clean_df['站點備註'] = clean_df.apply(get_source, axis=1)

    # --- A. 上方看板 (總銷量 & 更新時間) ---
    latest = df.iloc[-1]
    st.title("K-MONSTAR實時cut")
    
    c1, c2 = st.columns(2)
    c1.metric("當前總銷量", f"{int(latest['總銷量(累積)'])} 本")
    c2.metric("最近更新時間", str(latest['時刻']).split(".")[0]) # 只取到秒

    st.divider()

    # --- B. 極簡排行榜 ---
    st.subheader("每筆訂單")
    # 篩選掉 0 的成交，按銷量排序取前 15 名
    rank_df = clean_df[clean_df['每筆銷量(本次)'] > 0].sort_values(by='每筆銷量(本次)', ascending=False).head(15)

    if not rank_df.empty:
        # 只保留你要的欄位
        final_table = rank_df[['時刻', '每筆銷量(本次)', '站點備註']]
        final_table.columns = ['成交時間', '銷售數量', '來源']
        
        # 顯示表格
        st.table(final_table)
    else:
        st.info("目前尚無有效成交紀錄，等待數據寫入中...")

else:
    st.warning("試算表目前是空的。")
