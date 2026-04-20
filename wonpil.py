import streamlit as st
import pandas as pd
import plotly.express as px
import urllib.parse

# --- 配置區 ---
SHEET_ID = "11UXviXGiGJ33aRss2TdIL5b57vp8jrvqvjclK-TPkY8"
SHEET_NAME = "工作表1"

def get_data():
    # URL 編碼處理中文分頁名
    encoded_sheet_name = urllib.parse.quote(SHEET_NAME)
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={encoded_sheet_name}"
    
    # 讀取資料
    df = pd.read_csv(url)
    
    # 1. 處理時間格式：強制把「下午/上午」換成 PM/AM 才能解析
    df['時刻'] = df['時刻'].astype(str).str.replace('下午', ' PM').str.replace('上午', ' AM')
    df['時刻'] = pd.to_datetime(df['時刻'], errors='coerce')
    
    # 2. 資料清洗：確保變化量是純數字
    if '變化量' in df.columns:
        df['變化量'] = df['變化量'].astype(str).str.replace('+', '', regex=False).replace('紀錄更新', '0')
        df['變化量'] = pd.to_numeric(df['變化量'], errors='coerce').fillna(0)
    
    # 3. 確保總銷量也是數字
    df['總銷量'] = pd.to_numeric(df['總銷量'], errors='coerce').fillna(0)
    
    return df.dropna(subset=['時刻']).sort_values('時刻')

st.set_page_config(page_title="WONPIL 銷量實時監控", page_icon="📈", layout="wide")

st.title("📊 WONPIL 簽售銷量實時監控站")

try:
    df = get_data()
    
    if not df.empty:
        # --- 核心指標 ---
        latest = df.iloc[-1]
        c1, c2, c3 = st.columns(3)
        c1.metric("目前總銷量", f"{int(latest['總銷量'])} 張")
        c2.metric("最後更新時間", latest['時刻'].strftime('%m/%d %H:%M:%S'))
        c3.metric("上次增幅", f"+{int(latest['變化量'])} 張")

        # --- 即時排名：按變化量從大到小排 ---
        st.subheader("🔥 購買力單次排名 (Top 10)")
        # 只顯示有增加的紀錄，並按增加數量排序
        rank = df[df['變化量'] > 0].sort_values('變化量', ascending=False).head(10).copy()
        rank['時刻'] = rank['時刻'].dt.strftime('%m/%d %H:%M')
        rank = rank[['時刻', '總銷量', '變化量']].reset_index(drop=True)
        rank.index += 1
        st.table(rank)

        # --- 趨勢圖 ---
        st.subheader("📈 銷量增長趨勢")
        fig = px.line(df, x='時刻', y='總銷量', markers=True)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("等待試算表更新數據中...")

except Exception as e:
    st.error(f"解析失敗，這通常是試算表時間格式造成的。")
    st.write(f"系統訊息：{e}")

if st.button("手動重新整理"):
    st.rerun()
