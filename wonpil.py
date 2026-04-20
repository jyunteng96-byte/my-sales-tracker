import streamlit as st
import pandas as pd
import plotly.express as px
import urllib.parse

# --- 配置區 ---
SHEET_ID = "11UXviXGiGJ33aRss2TdIL5b57vp8jrvqvjclK-TPkY8"
SHEET_NAME = "工作表1"

def get_data():
    # URL 編碼處理
    encoded_sheet_name = urllib.parse.quote(SHEET_NAME)
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={encoded_sheet_name}"
    
    # 讀取資料
    df = pd.read_csv(url)
    
    # 【關鍵修正】不依賴名稱，直接用位置索引來命名 (確保相容性)
    # 第一欄: 時刻, 第二欄: 總銷量, 第三欄: 變化量
    df.columns = ['時刻', '總銷量', '變化量'] + list(df.columns[3:])
    
    # 1. 處理時間格式 (處理上午/下午問題)
    df['時刻'] = df['時刻'].astype(str).str.replace('下午', ' PM').str.replace('上午', ' AM')
    df['時刻'] = pd.to_datetime(df['時刻'], errors='coerce')
    
    # 2. 清洗數據：轉為數字並處理「紀錄更新」等文字
    df['變化量'] = df['變化量'].astype(str).str.replace('+', '', regex=False).replace('紀錄更新', '0')
    df['變化量'] = pd.to_numeric(df['變化量'], errors='coerce').fillna(0)
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
        c2.metric("最後更新時間", latest['時刻'].strftime('%Y/%m/%d %H:%M:%S'))
        c3.metric("上次增幅", f"+{int(latest['變化量'])} 張")

        # --- 購買力排行榜 ---
        st.subheader("🔥 購買力單次排名 (Top 10)")
        # 排除 0 的紀錄，並按變化量降序排
        rank = df[df['變化量'] > 0].sort_values('變化量', ascending=False).head(10).copy()
        if not rank.empty:
            rank['時刻顯示'] = rank['時刻'].dt.strftime('%m/%d %H:%M')
            display_df = rank[['時刻顯示', '總銷量', '變化量']].reset_index(drop=True)
            display_df.columns = ['時刻', '累積總量', '單次增加']
            display_df.index += 1
            st.table(display_df)
        else:
            st.write("目前尚無銷售增長紀錄。")

        # --- 趨勢圖 ---
        st.subheader("📈 銷量累積趨勢")
        fig = px.line(df, x='時刻', y='總銷量', markers=True)
        st.plotly_chart(fig, use_container_width=True)
        
    else:
        st.info("等待試算表更新數據中...")

except Exception as e:
    st.error("系統發生未知錯誤，請檢查試算表格式")
    st.write(f"系統訊息：{e}")

st.sidebar.button("手動重新整理")
