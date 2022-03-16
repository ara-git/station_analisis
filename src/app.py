"""
streamlit appのためのファイル
"""
import pandas as pd
import streamlit as st
import warnings
import logic

warnings.simplefilter("ignore")

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
station_name_list = [None] + list(station_data["station_name"])

# 駅名を入力する
input_station_name_list = []
input_station_name_list.append(st.sidebar.selectbox("駅1", station_name_list))
input_station_name_list.append(st.sidebar.selectbox("駅2", station_name_list))
input_station_name_list.append(st.sidebar.selectbox("駅3", station_name_list))
input_station_name_list.append(st.sidebar.selectbox("駅4", station_name_list))
input_station_name_list.append(st.sidebar.selectbox("駅5", station_name_list))
input_station_name_list.append(st.sidebar.selectbox("駅7", station_name_list))
input_station_name_list.append(st.sidebar.selectbox("駅8", station_name_list))

# Noneをリストから除く
input_station_name_list = list(filter(None, input_station_name_list))
# 重複を除く
input_station_name_list = list(set(input_station_name_list))

st.title("集合駅を決める")
st.write(input_station_name_list)

if len(input_station_name_list) != 0:
    # 中心を計算する
    # インスタンスを作成
    ins_center = logic.central_station(
        station_data, station_name_list, input_station_name_list
    )

    ###
    # 緯度経度ベース・合計値最小化で中心駅を求める
    st.header("合計移動距離を最小化する")
    (
        center_station_name,
        center_station_location,
    ) = ins_center.calc_center_location_sum()
    st.write(center_station_name)

    # 地図を開く
    ins_center.make_map()

    ###
    # 緯度経度ベース・最大値と最小値の差の最小化で中心駅を求める
    st.header("最大移動距離と最小移動距離を最小化する")
    (
        center_station_name,
        center_station_location,
    ) = ins_center.calc_center_location_fairness()
    st.write(center_station_name)

    # 地図を開く
    ins_center.make_map()

    ###
    # 料金ベース・合計値最大化で中心駅を求める
    (center_station_name, center_station_location,) = ins_center.calc_center_fare_sum()
    st.write(center_station_name)

    # 地図を開く
    ins_center.make_map()
