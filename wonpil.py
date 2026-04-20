import streamlit as st
import pandas as pd
import plotly.express as px
import urllib.parse  # 導入編碼工具

# --- 配置區 ---
SHEET_ID = "11UXviXGiGJ33aRss2TdIL5b57vp8jrvqvjclK-TPkY8"
SHEET_NAME = "工作表1"

def get_data():
    # 關鍵修正：將中文分頁名稱進行 URL 編碼
    encoded_sheet_name = urllib.parse.quote(SHEET_NAME)
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={encoded_sheet_name}"
    
    # 增加 encoding='utf-8' 確保讀取中文不報錯
    df = pd.read_csv(url, encoding='utf-8')
    
    # 資料清洗
    if '變化量' in df.columns:
        df['變化量'] = df['變化量'].astype(str).str.replace('+', '', regex=False).replace('紀錄更新', '0').astype(float)
    
    df['時刻'] = pd.to_datetime(df['時刻'])
    return df

st.set_page_config(page_title="WONPIL 銷量實時監控", page_icon="📈", layout="wide")

st.title("📊 WONPIL 簽售銷量實時監控站")

try:
    df = get_data()
    
    # --- 指標區 ---
    latest_row = df.iloc[-1]
    col1, col2, col3 = st.columns(3)
    col1.metric("目前總銷量", f"{int(latest_row['總銷量'])} 張")
    col2.metric("最後更新時間", latest_row['時刻'].strftime('%Y/%m/%d %H:%M:%S'))
    col3.metric("上次增幅", f"+{int(latest_row['變化量'])} 張")

    # --- 排名區 (按變化量降序) ---
    st.subheader("🔥 單次購買排行榜 (Top 10)")
    # 過濾掉變化量為 0 的紀錄，只排有買的
    ranking_df = df[df['變化量'] > 0].sort_values(by='變化量', ascending=False).head(10).copy()
    ranking_df = ranking_df[['時刻', '總銷量', '變化量']].reset_index(drop=True)
    ranking_df.index += 1
    st.table(ranking_df)

    # --- 圖表區 ---
    st.subheader("📈 銷量趨勢圖")
    fig = px.line(df, x='時刻', y='總銷量', markers=True)
    st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"連線失敗，請檢查權限或分頁名稱。")
    st.write(f"系統錯誤訊息: {e}")
