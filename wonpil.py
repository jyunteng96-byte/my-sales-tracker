import streamlit as st
import pandas as pd

# --- 設定區 ---
# 替換成你的 Google Sheet ID
SHEET_ID = "11UXviXGiGJ33aRss2TdIL5b57vp8jrvqvjclK-TPkY8"
# 指定工作表名稱
SHEET_NAME = "工作表1" 

def load_data():
    # 將 Google Sheet 轉換為 CSV 下載連結
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={SHEET_NAME}"
    df = pd.read_csv(url)
    
    # 確保變化量是數字（移除可能存在的 "+" 號）
    if '變化量' in df.columns:
        df['變化量'] = df['變化量'].astype(str).str.replace('+', '').astype(float)
    return df

st.set_page_config(page_title="WONPIL 銷量即時排名", layout="wide")

st.title("📊 WONPIL 簽售銷量即時監測")

try:
    df = load_data()

    # 1. 顯示目前的總銷量大指標
    latest_total = df['總銷量'].iloc[-1]
    st.metric(label="目前總銷量", value=f"{int(latest_total)} 張")

    # 2. 製作排名 (按變化量排序)
    st.subheader("🔥 變化量即時排名 (Top)")
    
    # 我們取最近的記錄來看看誰的增幅最大
    # 這裡可以根據時間分組，或是直接顯示最近幾次的變動
    ranking_df = df.sort_values(by='變化量', ascending=False).head(10)
    
    # 整理一下顯示的格式
    ranking_df = ranking_df[['時刻', '總銷量', '變化量']].reset_index(drop=True)
    ranking_df.index = ranking_df.index + 1 # 讓 index 從 1 開始變成排名
    
    # 顯示表格
    st.table(ranking_df)

    # 3. 視覺化圖表
    st.subheader("📈 銷量增長趨勢")
    st.line_chart(df.set_index('時刻')['總銷量'])

except Exception as e:
    st.error(f"資料抓取失敗，請確認試算表已開啟共用權限。")
    st.info("錯誤訊息: " + str(e))

# 每 60 秒自動重新整理
if st.button('手動重新整理'):
    st.rerun()
