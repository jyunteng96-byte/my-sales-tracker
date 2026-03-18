import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="K-MONSTAR 實時cut", layout="centered")
st.title("K-MONSTAR 實時cut ")

# 連線試算表
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(ttl=0)
except Exception as e:
    st.error("連線失敗，請檢查 Secrets 設定。")
    st.stop()

if not df.empty:
    # 轉換數值
    for col in ['台灣差值', '國外差值', '每筆銷量(本次)']:
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

    # --- 整理極簡排行榜 ---
    # 1. 判斷來源
    def get_source(row):
        if row['台灣差值'] > 0 and row['國外差值'] > 0: return "雙站同時"
        elif row['台灣差值'] > 0: return "台灣"
        elif row['國外差值'] > 0: return "國際"
        return "無變動"

    clean_df['來源備註'] = clean_df.apply(get_source, axis=1)
    
    # 2. 篩選有成交的紀錄並排序
    rank_df = clean_df[clean_df['每筆銷量(本次)'] > 0].sort_values(by='每筆銷量(本次)', ascending=False).head(15)

    if not rank_df.empty:
        # 只保留你要的：時間、每筆銷量、來源備註
        final_display = rank_df[['時刻', '每筆銷量(本次)', '來源備註']]
        final_display.columns = ['成交時間', '銷售數量', '站點備註']
        
        # 顯示表格
        st.table(final_display)
    else:
        st.info("目前尚無有效成交紀錄。")

    st.divider()
    # 底部顯示一個小總計就好
    latest = df.iloc[-1]
    st.caption(f"最後更新：{latest['時刻']} | 目前兩站總計：{int(latest['總銷量(累積)'])} 本")

else:
    st.warning("試算表目前無數據。")
