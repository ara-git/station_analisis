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
st.write("最寄駅を入力し、最適な集合駅を計算します。詳細は")
st.write("https://github.com/ara-git/station_analysis")
st.write("を参照してください。")
if len(input_station_name_list) >= 2:
    # 中心を計算する
    # インスタンスを作成
    ins_center = logic.central_station(
        station_data, station_name_list, input_station_name_list
    )

    ###
    # 緯度経度ベース・合計値最小化で中心駅を求める
    st.header("合計直線距離を最小化する")
    (
        center_station_name,
        center_station_location,
    ) = ins_center.calc_center_location_sum()
    st.write("集合駅：", center_station_name)

    # 地図を開く
    ins_center.make_map()

    ###
    # 緯度経度ベース・最大値と最小値の差の最小化で中心駅を求める
    st.header("最大直線距離と最小直線距離の差を最小化する")
    (
        center_station_name,
        center_station_location,
    ) = ins_center.calc_center_location_fairness()
    st.write("集合駅：", center_station_name)

    # 地図を開く
    ins_center.make_map()

    ###
    # 料金ベース・合計値最小化で中心駅を求める
    st.header("合計費用を最小化する")
    (
        center_station_name,
        center_station_location,
        optimal_fare_df,
        min_of_sum,
    ) = ins_center.calc_center_fare_sum()

    st.write("集合駅：", center_station_name)
    st.write("合計費用:", min_of_sum, "円")
    st.table(optimal_fare_df)

    # 地図を開く
    ins_center.make_map()

    ###
    # 料金ベース・最大値と最小値の差の最小化で中心駅を求める
    st.header("最大費用と最小費用の差を最小化する")
    (
        center_station_name,
        center_station_location,
        optimal_fare_df,
        min_of_dif_fare,
    ) = ins_center.calc_center_fare_fairness()

    st.write("集合駅：", center_station_name)
    st.write("最大費用と最小費用の差：", min_of_dif_fare, "円")
    st.table(optimal_fare_df)

    # 地図を開く
    ins_center.make_map()

else:
    st.header("左のサイドバーに駅名を入力して下さい")
