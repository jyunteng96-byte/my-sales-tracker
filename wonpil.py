import streamlit as st
import pandas as pd
import urllib.parse

# --- 配置區 ---
SHEET_ID = "11UXviXGiGJ33aRss2TdIL5b57vp8jrvqvjclK-TPkY8"
SHEET_NAME = "工作表1"

def get_data():
    encoded_sheet_name = urllib.parse.quote(SHEET_NAME)
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={encoded_sheet_name}"
    
    # 讀取 CSV，skiprows=0 確保從頭讀取，但我們會手動處理標題
    df = pd.read_csv(url)
    
    # 【關鍵修正 1】只取前三欄，並強制命名，不讓 Google 的編碼干擾
    df = df.iloc[:, :3]
    df.columns = ['時刻', '總銷量', '變化量']
    
    # 【關鍵修正 2】清洗時間格式 (處理上午/下午)
    df['時刻'] = df['時刻'].astype(str).str.replace('下午', ' PM').str.replace('上午', ' AM')
    df['時刻'] = pd.to_datetime(df['時刻'], errors='coerce')
    
    # 【關鍵修正 3】清洗數字：移除符號，轉換失敗的變 0
    df['變化量'] = df['變化量'].astype(str).str.replace('+', '', regex=False).replace('紀錄更新', '0')
    df['變化量'] = pd.to_numeric(df['變化量'], errors='coerce').fillna(0)
    df['總銷量'] = pd.to_numeric(df['總銷量'], errors='coerce').fillna(0)
    
    # 刪除掉轉換失敗的日期行 (避免抓到標題列)
    df = df.dropna(subset=['時刻'])
    
    # 【關鍵修正 4】異常數據過濾
    # 如果單次增加量大到不合理 (例如 > 1000)，通常是公式對錯行，直接排除
    df = df[df['變化量'] < 1000]
    
    return df.sort_values('時刻')

st.set_page_config(page_title="購買量排行", page_icon="📊", layout="wide")

st.title("📊 購買量排行")

try:
    df = get_data()
    
    if not df.empty:
        latest = df.iloc[-1]
        c1, c2 = st.columns(2)
        # 顯示最後一行真實的總量
        c1.metric("目前累積總量", f"{int(latest['總銷量'])} 張")
        c2.metric("最後更新時間", latest['時刻'].strftime('%Y/%m/%d %H:%M:%S'))

        st.markdown("---")

        # --- 全部排名 (排除 0 且按購買量降序) ---
        all_rank = df[df['變化量'] > 0].sort_values('變化量', ascending=False).copy()
        
        if not all_rank.empty:
            all_rank['交易時刻'] = all_rank['時刻'].dt.strftime('%m/%d %H:%M:%S')
            display_df = all_rank[['交易時刻', '總銷量', '變化量']].reset_index(drop=True)
            display_df.columns = ['交易時刻', '當時累積總量', '單次購買量']
            display_df.index += 1
            
            st.dataframe(display_df, use_container_width=True, height=800)
        else:
            st.info("目前尚未偵測到任何購買紀錄。")
            
    else:
        st.warning("試算表內沒有有效的數據，請檢查內容。")

except Exception as e:
    st.error("數據解析崩潰中...")
    st.write(f"錯誤代碼：{e}")

if st.button("手動刷新"):
    st.rerun()
