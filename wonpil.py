import streamlit as st
import pandas as pd
import urllib.parse
import time

# --- 基礎配置 (使用您提供的正確 ID) ---
SHEET_ID = "1LT9LH5M9q7fx7Or_ZvYIeQEcndjyfOKqqDlC-kMMz9k"
SHEET_NAME = "工作表1"

def get_data():
    encoded_sheet_name = urllib.parse.quote(SHEET_NAME)
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={encoded_sheet_name}&t={int(time.time())}"
    
    # 直接讀取，不解析日期以確保 100% 同步
    df = pd.read_csv(url)
    df = df.iloc[:, :3]
    df.columns = ['時刻', '總銷量', '變化量']
    
    # 數字清洗
    df['變化量'] = pd.to_numeric(df['變化量'].astype(str).str.replace('+', '', regex=False), errors='coerce').fillna(0)
    df['總銷量'] = pd.to_numeric(df['總銷量'], errors='coerce').fillna(0)
    
    return df.dropna(subset=['時刻'])

# 定義顏色邏輯的函數
def highlight_rows(row):
    rank = row.name + 1 # row.name 是從 0 開始的索引
    if 1 <= rank <= 50:
        return ['background-color: #ffcccc'] * len(row) # 紅色底
    elif 51 <= rank <= 150:
        return ['background-color: #cce5ff'] * len(row) # 藍色底
    else:
        return [''] * len(row)

st.set_page_config(page_title="購買量排行", layout="wide")
st.title("📊 購買量排行")

try:
    df = get_data()
    
    if not df.empty:
        # 指標區 (顯示表底最新一筆)
        latest = df.iloc[-1]
        c1, c2 = st.columns(2)
        c1.metric("目前累積總量", f"{int(latest['總銷量'])} 張")
        c2.metric("最後更新時刻", str(latest['時刻']))

        st.markdown("---")

        # --- 購買量排行排序 ---
        rank_df = df[df['變化量'] > 0].sort_values('變化量', ascending=False).copy()
        
        if not rank_df.empty:
            # 整理顯示欄位
            display_df = rank_df[['時刻', '總銷量', '變化量']].reset_index(drop=True)
            display_df.columns = ['交易時刻', '累積總量', '購買量']
            
            # 設定排名序號 (從 1 開始)
            display_df.index += 1
            
            # 套用顏色樣式
            # 這裡使用 st.dataframe 因為 st.table 不支援複雜的 style 渲染
            styled_df = display_df.reset_index().rename(columns={'index': '排名'})
            
            # 應用顏色邏輯 (注意：此時 '排名' 已經是 DataFrame 的第一欄)
            def color_apply(val):
                rank = val.name + 1
                if 1 <= rank <= 50:
                    return ['background-color: #FF4B4B; color: white'] * len(val) # 紅底白字
                elif 51 <= rank <= 150:
                    return ['background-color: #1F77B4; color: white'] * len(val) # 藍底白字
                return [''] * len(val)

            st.write("### 完整排名清單")
            st.dataframe(
                styled_df.style.apply(color_apply, axis=1),
                use_container_width=True,
                height=1000 # 設置高度讓全部排名更易於查看
            )
        else:
            st.info("目前尚無購買紀錄。")
            
    else:
        st.error("讀取失敗，請確認分頁名稱。")

except Exception as e:
    st.error(f"系統故障：{e}")

if st.sidebar.button("手動刷新"):
    st.rerun()
