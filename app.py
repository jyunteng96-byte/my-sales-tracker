import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="K-MONSTAR 即時戰報", layout="wide")
st.title("🏆 K-MONSTAR 應募銷量排行榜")

# 1. 建立連線
conn = st.connection("gsheets", type=GSheetsConnection)
df = conn.read(ttl=0) 

if not df.empty:
    # 數值轉換
    cols = ['台灣總銷量', '台灣差值', '國外總銷量', '國外差值', '總銷量(累積)', '每筆銷量(本次)']
    for col in cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # --- 核心功能：抵銷退單 ---
    # 邏輯：如果有一筆 +1，後面出現一筆 -1，則兩筆都標記為無效
    valid_indices = list(df.index)
    
    # 檢查台灣站退單
    for i in df[df['台灣差值'] < 0].index:
        cancel_val = abs(df.loc[i, '台灣差值'])
        # 尋找前面最近一筆相同的正數
        match = df[(df.index < i) & (df['台灣差值'] == cancel_val) & (df.index.isin(valid_indices))].last_valid_index()
        if match is not None:
            valid_indices.remove(i)
            valid_indices.remove(match)

    # 檢查國外站退單
    for i in df[df['國外差值'] < 0].index:
        cancel_val = abs(df.loc[i, '國外差值'])
        match = df[(df.index < i) & (df['國外差值'] == cancel_val) & (df.index.isin(valid_indices))].last_valid_index()
        if match is not None:
            if i in valid_indices: valid_indices.remove(i)
            if match in valid_indices: valid_indices.remove(match)

    # 過濾後的數據
    clean_df = df.loc[valid_indices].copy()

    # --- 顯示介面 ---
    latest = df.iloc[-1]
    c1, c2, c3 = st.columns(3)
    c1.metric("🔥 總銷量", f"{int(latest['總銷量(累積)'])} 本")
    c2.metric("🇹🇼 台灣站", f"{int(latest['台灣總銷量'])} 本", f"{int(latest['台灣差值'])}")
    c3.metric("🌐 國際站", f"{int(latest['國外總銷量'])} 本", f"{int(latest['國外差值'])}")

    st.divider()

    # 排行榜 (使用過濾後的數據)
    st.subheader("🥇 每筆成交衝刺榜 (已自動扣除退單)")
    rank_df = clean_df[clean_df['每筆銷量(本次)'] > 0].sort_values(by='每筆銷量(本次)', ascending=False).head(10)
    
    if not rank_df.empty:
        show_df = rank_df[['時刻', '台灣差值', '國外差值', '每筆銷量(本次)']]
        show_df.columns = ['成交時間', '台灣+', '國外+', '合計成交']
        st.table(show_df)
    else:
        st.write("目前尚無有效成交紀錄。")

    with st.expander("查看原始數據 (含退單紀錄)"):
        st.dataframe(df.sort_values(by='時刻', ascending=False))
else:
    st.info("等待數據寫入中...")