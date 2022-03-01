"""
streamlit appのためのファイル
"""
import os
import pandas as pd
import streamlit as st

# 駅データを読み込む
##関東三県に対応
tokyo = pd.read_csv(
    filepath_or_buffer="./data/station_name/駅_東京.csv", encoding="ms932", sep=","
)
saitama = pd.read_csv(
    filepath_or_buffer="./data/station_name/駅_埼玉.csv", encoding="ms932", sep=","
)
kanagawa = pd.read_csv(
    filepath_or_buffer="./data/station_name/駅_神奈川.csv", encoding="ms932", sep=","
)

station_data = tokyo.append(saitama).append(kanagawa)

# 駅名をリスト化
station_name_list = list(station_data["station_name"])

st.sidebar.selectbox("駅1", station_name_list)
