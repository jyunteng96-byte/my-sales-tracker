import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 網頁設定
st.set_page_config(page_title="合照實時cut", layout="centered")
st.title("K-MONSTAR合照實時cut")

# 1. 建立連線
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(ttl=0)
except Exception as e:
    st.error("連線失敗，請檢查此 App 的 Secrets 設定。")
    st.stop()

if not df.empty:
    # 數值轉換
    for col in ['台灣差值', '國外差值', '每筆銷量(本次)', '總銷量(累積)']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # --- 抵銷退單邏輯 ---
    valid_indices = list(df.index)
    for i in df[df['台灣差值'] < 0].index:
        val = abs(df.loc[i, '台灣差值'])
        match = df[(df.index < i) & (df['台灣差值'] == val) & (df.index.isin(valid_indices))].last_valid_index()
        if match is not None:
            valid_indices.remove(i); valid_indices.remove(match)

    clean_df = df.loc[valid_indices].copy()

    # --- 顯示上方看板 ---
    latest = df.iloc[-1]
    c1, c2 = st.columns(2)
    c1.metric("當前總銷量", f"{int(latest['總銷量(累積)'])} 本")
    c2.metric("最近更新時間", str(latest['時刻']).split(".")[0])

    st.divider()

    # --- 顯示極簡排行榜 ---
    st.subheader("每筆成交排行榜")
    rank_df = clean_df[clean_df['每筆銷量(本次)'] > 0].sort_values(by='每筆銷量(本次)', ascending=False).head(15)
    
    if not rank_df.empty:
        final_table = rank_df[['時刻', '每筆銷量(本次)']]
        final_table.columns = ['成交時間', '銷售數量']
        st.table(final_table)
    else:
        st.info("等待新活動數據寫入中...")
else:
    st.warning("試算表目前無數據。")
