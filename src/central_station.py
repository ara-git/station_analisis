# とりあえず距離ベースで考える。
##関東三県に対応

import os
import numpy as np
import pandas as pd
import math
from matplotlib import pyplot as plt
import functions as func

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

# 関数を実行し、中心を求める。
##駅名を入力する
# Station_name = func.input_station_name(station_data)
Station_name = ["東京", "青梅", "横浜", "川口"]

##計算する
res_center = func.calc_center(Station_name, station_data)
(
    Station_name,
    Input_location,
    Center_location,
    Center_station_name,
    Center_station_location,
) = res_center


print("中心の駅：", Center_station_name)

m = func.make_map(
    station_data,
    Station_name,
    Input_location,
    Center_location,
    Center_station_name,
    Center_station_location,
)
m.save("map.html")

# ここから、料金ベースでの中心を求める。
##料金データ（csv）を読み込むs
Fare = pd.read_csv(
    "./data/fare/fare_all.csv", encoding="shift jis", index_col="Unnamed: 0"
)

# 料金の合計値を最小にするような駅を計算する
res_center2 = func.calc_center_fare_sum(Station_name, station_data, Fare)
(
    Station_name,
    Input_location,
    Center_station_name,
    Center_station_location,
    min_of_sum,
) = res_center2
print("中心の駅, 料金ベース, 合計値最小：", Center_station_name)

m = func.make_map(
    station_data,
    Station_name,
    Input_location,
    Center_location,
    Center_station_name,
    Center_station_location,
)
m.save("map2.html")

# 料金の最大値を最小にするような駅を計算する
res_center3 = func.calc_center_fare_min(Station_name, station_data, Fare)
(
    Station_name,
    Input_location,
    Center_station_name,
    Center_station_location,
    min_of_max,
) = res_center3
print("中心の駅, 料金ベース, 合計値最小：", Center_station_name)

m = func.make_map(
    station_data,
    Station_name,
    Input_location,
    Center_location,
    Center_station_name,
    Center_station_location,
)
m.save("map3.html")
