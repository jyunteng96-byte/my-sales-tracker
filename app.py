import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 1. 網頁基本設定
st.set_page_config(page_title="K-MONSTAR 雙站即時戰報", layout="wide")

# 2. 標題與風格
st.title("🏆 K-MONSTAR 應募銷量排行榜")
st.caption("同步追蹤台灣與國際站數據 | 有成交變動時自動更新")

# 3. 建立試算表連線
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    # ttl=0 確保每次重新整理都會抓取最新數據，不使用快取
    df = conn.read(ttl=0) 
except Exception as e:
    st.error(f"連線試算表失敗，請檢查 Secrets 設定。錯誤訊息: {e}")
    st.stop()

if not df.empty:
    # 確保數值欄位格式正確，避免運算錯誤
    numeric_cols = ['台灣總銷量', '台灣差值', '國外總銷量', '國外差值', '總銷量(累積)', '每筆銷量(本次)']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    # 取得最新一筆數據（最後一行）
    latest = df.iloc[-1]
    
    # --- A. 上方大數字看板 ---
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🔥 總累計銷量", f"{int(latest['總銷量(累積)'])} 本")
    with col2:
        # 顯示台灣總銷，並標註本次增加了多少
        st.metric("🇹🇼 台灣站累計", f"{int(latest['台灣總銷量'])} 本", f"+{int(latest['台灣差值'])}")
    with col3:
        # 顯示國外總銷，並標註本次增加了多少
        st.metric("🌐 國際站累計", f"{int(latest['國外總銷量'])} 本", f"+{int(latest['國外差值'])}")

    st.divider()

    # --- B. 銷量衝刺排行榜 (依據「每筆銷量」排序) ---
    st.subheader("🥇 每筆成交衝刺榜 (Top 10)")
    st.write("以下為單次抓取中，兩站合計增加最多的成交紀錄：")

    # 邏輯：排除掉差值為 0 的紀錄，並按「每筆銷量(本次)」從大到小排序
    if '每筆銷量(本次)' in df.columns:
        rank_df = df[df['每筆銷量(本次)'] > 0].sort_values(by='每筆銷量(本次)', ascending=False).head(10)
        
        if not rank_df.empty:
            # 整理要顯示的欄位名
            display_df = rank_df[['時刻', '台灣差值', '國外差值', '每筆銷量(本次)']].copy()
            display_df.columns = ['成交時間', '台灣增加', '國外增加', '該筆合計銷量']
            
            # 加上名次裝飾
            medals = ['🥇', '🥈', '🥉', '4', '5', '6', '7', '8', '9', '10']
            display_df.insert(0, '排名', medals[:len(display_df)])
            
            # 使用 table 顯示
            st.table(display_df.set_index('排名'))
        else:
            st.info("目前尚未偵測到任何銷量增加的紀錄。")
    
    st.divider()

    # --- C. 完整數據時間軸 ---
    with st.expander("📂 查看完整歷史成交紀錄"):
        # 按時間倒序排列（最新的在上面）
        st.dataframe(df.sort_values(by='時刻', ascending=False), use_container_width=True)

else:
    st.warning("💡 試算表目前是空的。請先在 Google Apps Script 執行一次抓取，或檢查試算表權限！")

# 頁面底部自動重新整理按鈕
if st.button('🔄 立即更新數據'):
    st.rerun()