import streamlit as st
import pandas as pd
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
    
    # 強制按位置命名欄位，解決編碼識別問題
    df.columns = ['時刻', '總銷量', '變化量'] + list(df.columns[3:])
    
    # 處理時間格式
    df['時刻'] = df['時刻'].astype(str).str.replace('下午', ' PM').str.replace('上午', ' AM')
    df['時刻'] = pd.to_datetime(df['時刻'], errors='coerce')
    
    # 清洗數據
    df['變化量'] = df['變化量'].astype(str).str.replace('+', '', regex=False).replace('紀錄更新', '0')
    df['變化量'] = pd.to_numeric(df['變化量'], errors='coerce').fillna(0)
    df['總銷量'] = pd.to_numeric(df['總銷量'], errors='coerce').fillna(0)
    
    return df.dropna(subset=['時刻']).sort_values('時刻')

st.set_page_config(page_title="購買量排行", page_icon="📊", layout="wide")

# 修改標題
st.title("📊 購買量排行")

try:
    df = get_data()
    
    if not df.empty:
        # 顯示當前總計指標
        latest = df.iloc[-1]
        c1, c2 = st.columns(2)
        c1.metric("目前累積總量", f"{int(latest['總銷量'])} 張")
        c2.metric("最後更新時間", latest['時刻'].strftime('%Y/%m/%d %H:%M:%S'))

        st.markdown("---")

        # --- 全部排名 (按變化量降序) ---
        # 篩選掉變化量為 0 的資料，顯示所有大於 0 的紀錄
        all_rank = df[df['變化量'] > 0].sort_values('變化量', ascending=False).copy()
        
        if not all_rank.empty:
            all_rank['時刻顯示'] = all_rank['時刻'].dt.strftime('%m/%d %H:%M:%S')
            # 整理顯示表格
            display_df = all_rank[['時刻顯示', '總銷量', '變化量']].reset_index(drop=True)
            display_df.columns = ['交易時刻', '累積總銷量', '單次購買量']
            display_df.index += 1  # 排名從 1 開始
            
            # 使用 st.dataframe 顯示完整清單，這可以滾動查看全部
            st.dataframe(display_df, use_container_width=True, height=600)
        else:
            st.info("目前尚未偵測到任何購買變動紀錄。")
            
    else:
        st.info("資料讀取中，請稍候...")

except Exception as e:
    st.error("讀取失敗，請確認試算表格式。")
    st.write(f"系統訊息：{e}")

# 側邊欄重新整理按鈕
if st.sidebar.button("立即刷新數據"):
    st.rerun()
