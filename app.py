import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 網頁設定
st.set_page_config(page_title="K-MONSTAR實時數據", layout="wide")
st.title("K-MONSTAR實時數據")

# 1. 建立連線
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(ttl=0) 
except Exception as e:
    st.error(f"連線失敗，請檢查 Secrets。錯誤: {e}")
    st.stop()

if not df.empty:
    # 數值轉換
    cols = ['台灣總銷量', '台灣差值', '國外總銷量', '國外差值', '總銷量(累積)', '每筆銷量(本次)']
    for col in cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # --- 核心功能：抵銷退單 ---
    valid_indices = list(df.index)
    # 檢查台灣站退單 (+1 與 -1 抵銷)
    for i in df[df['台灣差值'] < 0].index:
        cancel_val = abs(df.loc[i, '台灣差值'])
        match = df[(df.index < i) & (df['台灣差值'] == cancel_val) & (df.index.isin(valid_indices))].last_valid_index()
        if match is not None:
            valid_indices.remove(i)
            valid_indices.remove(match)

    # 過濾後的數據
    clean_df = df.loc[valid_indices].copy()

    # --- 顯示介面 ---
    latest = df.iloc[-1]
    c1, c2, c3 = st.columns(3)
    c1.metric("總銷量", f"{int(latest['總銷量(累積)'])} 本")
    c2.metric("台灣", f"{int(latest['台灣總銷量'])} 本", f"{int(latest['台灣差值'])}")
    c3.metric("國際", f"{int(latest['國外總銷量'])} 本", f"{int(latest['國外差值'])}")

    st.divider()

    # 排行榜 (使用過濾後的數據)
    st.subheader("每筆訂單 (已自動扣除退單)")
    if '每筆銷量(本次)' in clean_df.columns:
        rank_df = clean_df[clean_df['每筆銷量(本次)'] > 0].sort_values(by='每筆銷量(本次)', ascending=False).head(10)
        if not rank_df.empty:
            show_df = rank_df[['時刻', '台灣差值', '國外差值', '每筆銷量(本次)']]
            show_df.columns = ['成交時間', '台灣+', '國外+', '合計成交']
            st.table(show_df)
        else:
            st.write("目前尚無有效成交紀錄。")

    with st.expander("查看原始數據"):
        st.dataframe(df.sort_values(by='時刻', ascending=False))
else:
    st.info("💡 試算表目前是空的，請先在 GAS 執行一次抓取！")
