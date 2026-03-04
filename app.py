import streamlit as st
import pandas as pd

# 1. 網頁基本設定
st.set_page_config(page_title="ALLDAY PROJECT 結案報告", layout="wide")

st.title("ALLDAY PROJECT 活動結案")
st.success("本次活動已結束")
st.divider()

# 2. 【核心修改】將最終數據直接寫死在程式碼中
# 請根據你目前網頁上的最後顯示數值，填入下方的資料
final_total_sales = 192  # 填入最終總銷量
final_stock = 999808     # 填入最終剩餘庫存
final_update_time = "2026/02/24 11:32:30" # 填入最後更新時間

# 3. 顯示大數字看板 (不再讀取試算表)
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="最終總銷量", value=final_total_sales)
with col2:
    st.metric(label="剩餘總庫存", value=final_stock)
with col3:
    st.metric(label="活動結束時間", value=final_update_time)

st.divider()

# 4. 如果你想保留排行榜數據，建議手動輸入前幾名
st.subheader("銷量衝刺排行榜")

# 這裡建議你直接把網頁上現在的前 10 名數據手動打進去
ranking_data = {
    "排名": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    "更新時間": [
        "2026/02/24 09:45:30", "2026/02/24 09:49:29", "2026/02/24 11:32:30",
        "2026/02/24 10:06:29", "2026/02/24 10:39:30", "2026/02/24 10:26:30",
        "2026/02/24 10:48:29", "2026/02/24 10:30:30", "2026/02/24 09:48:29", "2026/02/24 09:50:30"
    ],
    "增長量": ["+5", "+5", "+5", "+5", "+1", "+1", "+1", "+1", "+-5", "+-5"]
}

df_static = pd.DataFrame(ranking_data)
st.table(df_static) # 使用靜態表格顯示，看起來更像報告

st.caption("本頁面為歷史紀錄，數據不再更新。")
