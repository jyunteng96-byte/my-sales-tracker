import streamlit as st
import pandas as pd
import urllib.parse
import time

# --- 配置區 ---
SHEET_ID = "11UXviXGiGJ33aRss2TdIL5b57vp8jrvqvjclK-TPkY8"
SHEET_NAME = "工作表1"

def get_data():
    # 加入時間戳記 t={int(time.time())} 強制跳過 Google 快取，確保讀到 4 月最新數據
    encoded_sheet_name = urllib.parse.quote(SHEET_NAME)
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={encoded_sheet_name}&t={int(time.time())}"
    
    # 讀取 CSV
    df = pd.read_csv(url)
    
    # 只取前三欄：時刻、總銷量、變化量
    df = df.iloc[:, :3]
    df.columns = ['時刻', '總銷量', '變化量']
    
    # 清洗時間格式
    df['時刻'] = df['時刻'].astype(str).str.replace('下午', ' PM').str.replace('上午', ' AM')
    df['時刻'] = pd.to_datetime(df['時刻'], errors='coerce')
    
    # 排除日期解析失敗的行 (髒數據)
    df = df.dropna(subset=['時刻'])
    
    # 清洗數字格式
    df['變化量'] = pd.to_numeric(df['變化量'].astype(str).str.replace('+', '', regex=False).replace('紀錄更新', '0'), errors='coerce').fillna(0)
    df['總銷量'] = pd.to_numeric(df['總銷量'], errors='coerce').fillna(0)
    
    # 【核心修正】只保留 4 月份或最近 3 天的資料，剔除 3 月的舊測試數據
    current_time = pd.Timestamp.now()
    df = df[df['時刻'] > (current_time - pd.Timedelta(days=3))]
    
    return df.sort_values('時刻')

st.set_page_config(page_title="購買量排行", page_icon="📊", layout="wide")
st.title("📊 購買量排行")

try:
    df = get_data()
    
    if not df.empty:
        latest = df.iloc[-1]
        c1, c2 = st.columns(2)
        c1.metric("目前累積總量", f"{int(latest['總銷量'])} 張")
        c2.metric("最後更新時間", latest['時刻'].strftime('%Y/%m/%d %H:%M:%S'))

        st.markdown("---")

        # 排行榜：顯示所有購買變動 (變化量 > 0)
        all_rank = df[df['變化量'] > 0].sort_values('變化量', ascending=False).copy()
        
        if not all_rank.empty:
            all_rank['交易時刻'] = all_rank['時刻'].dt.strftime('%m/%d %H:%M:%S')
            display_df = all_rank[['交易時刻', '總銷量', '變化量']].reset_index(drop=True)
            display_df.columns = ['交易時刻', '當時累積總量', '單次購買量']
            display_df.index += 1
            
            st.dataframe(display_df, use_container_width=True, height=800)
        else:
            st.info("近 3 天內尚未偵測到新的購買紀錄。")
            
    else:
        st.warning("⚠️ 沒找到最近 3 天的數據。請確認試算表內最新一筆資料的時間是否正確。")

except Exception as e:
    st.error("數據解析失敗")
    st.write(f"系統訊息：{e}")

if st.button("手動重新刷新"):
    st.rerun()
