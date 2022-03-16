# とりあえず距離ベースで考える。
##関東三県に対応

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import streamlit as st
import scipy.optimize

from streamlit_folium import folium_static
import folium


class central_station:
    def __init__(self, station_data, input_station_name):
        self.station_data = station_data
        self.input_station_name = input_station_name
        self.n = len(self.input_station_name)

        # 駅名を検索して、緯度と経度を取得
        self.input_location_list = []
        for name in self.input_station_name:
            each_station_data = self.station_data[
                self.station_data["station_name"] == name
            ]
            ido = np.array(each_station_data["station_lat"])
            keido = np.array(each_station_data["station_lon"])
            self.input_location_list.append([ido[0], keido[0]])

        # DF形式に変更
        self.input_location_df = pd.DataFrame(
            self.input_location_list, columns=["lat", "lon"]
        )

        ##料金データ（csv）を読み込む
        self.fare_df = pd.read_csv(
            "./data/fare/fare_all.csv", encoding="shift jis", index_col="Unnamed: 0"
        )

    def calc_center_location_sum(self):
        """
        駅名を入力し、中心の座標とそこから近い駅（の名前と座標）を出力する関数
        
        Returns
            Station_name：入力した駅名
            Input_location：入力した駅の緯度経度（リストのリスト）
            Center_location：中心地点の緯度経度（リスト）
            Ceneter_station_name：中心地点から近い駅名
            Center_station_location：中心地点から近い駅の緯度経度（リスト）
        """
        # 中心の緯度経度を求める
        # 重心を求める
        center_location_list = np.average(self.input_location_list, axis=0)

        # 重心からの最寄駅を求める
        self._search_nearest_station(center_location_list)
        return (
            self.center_station_name,
            self.center_station_location,
        )

    def calc_center_location_fairness(self):
        """
        最大移動距離と最小移動距離の差を最小化する（公平な場所）
        n >= 3の時はscipyの最適化関数を使う
        n = 2の時は一意に定まらないので、中点を使う
        """
        # 入力を設定
        input_lat = np.array(self.input_location_df["lat"])
        input_lon = np.array(self.input_location_df["lon"])

        # 最適な座標を計算する
        ## 初期値を設定する
        coordinate = [35, 140]
        ## 計算する
        if self.n == 2:
            center_location_list = np.average(self.input_location_list, axis=0)
        else:
            center_location_list = scipy.optimize.fmin_bfgs(
                f=self._objective_function, x0=coordinate, args=(input_lat, input_lon)
            )
        """
        # n== 3の時は 外心を計算する
        if self.n == 3:
            center_location_list = self._circumcenter(
                list(self.input_location_df.iloc[0, :]),
                list(self.input_location_df.iloc[1, :]),
                list(self.input_location_df.iloc[2, :]),
            )
            st.write("外心:", center_location_list)
        """
        # 中心からの最寄駅を求める
        self._search_nearest_station(center_location_list)
        return (
            self.center_station_name,
            self.center_station_location,
        )

    def _search_nearest_station(self, center_location_list):
        """
        緯度と経度のリストから最寄駅を計算する
        Augs
            求めたい緯度と経度のリスト
        Return
            self.center_station_name:最寄駅の名前
            self.center_station_location:最寄駅の緯度経度
        """

        # 中心から最も近い駅を求める
        min_index = np.argmin(
            (self.station_data["station_lat"] - center_location_list[0]) ** 2
            + (self.station_data["station_lon"] - center_location_list[1]) ** 2
        )
        center_station = self.station_data.iloc[min_index]
        self.center_station_name = center_station["station_name"]

        center_station_ido = center_station["station_lat"]
        center_station_keido = center_station["station_lon"]
        self.center_station_location = [center_station_ido, center_station_keido]

    def _objective_function(self, coordinate, input_lat, input_lon):
        """目的関数"""
        x = coordinate[0]
        y = coordinate[1]

        distance_list = (input_lat - x) ** 2 + (input_lon - y) ** 2
        unfairness = max(distance_list) - min(distance_list)

        return unfairness

    # 1 2つの長さを求める
    def _length(self, p1, p2):
        s = 0
        for i, j in zip(p1, p2):
            s += (i - j) ** 2
        return s ** 0.5

    # 2 三角形の3つの座標から3辺の長さを求める
    def _tri(self, pa, pb, pc):
        a = self._length(pc, pb)
        b = self._length(pa, pc)
        c = self._length(pa, pb)
        return a, b, c

    # 3 三角形の3つの座標からヘロンの公式を使い面積を求める
    def _square(self, a, b, c):
        s = (a + b + c) / 2
        return (s * (s - a) * (s - b) * (s - c)) ** 0.5

    # 4 三角形の3つの長さから、1番目の引数の角のsinの値を求める
    def _sin_l(self, a, b, c):
        s = self._square(a, b, c)
        return s * 2 / b / c

    # 5 三角形の3つの長さから、1番目の引数の角のcosの値を求める
    def _cos_l(self, a, b, c):
        return (b ** 2 + c ** 2 - a ** 2) / (2 * b * c)

    # 6 原点から2つの点となす角のsinの値を求める
    def _sin_v(self, p1, p2):
        a, b, c = self._tri((0, 0), p1, p2)
        return self.sin_l(a, b, c)

    # 7 原点から2つの点となす角のcosの値を求める
    def _cos_v(self, p1, p2):
        a, b, c = self.tri((0, 0), p1, p2)
        return self._cos_l(a, b, c)

    # 8 三角形の3つの座標から3つの角のsinの値を求める
    def _sin_t(self, pa, pb, pc):
        a, b, c = self._tri(pa, pb, pc)
        s = self._square(a, b, c)
        return s * 2 / b / c, s * 2 / c / a, s * 2 / a / b

    # 9 三角形の3つの座標から3つの角のcosの値を求める
    def _cos_t(self, pa, pb, pc):
        a, b, c = self._tri(pa, pb, pc)
        return self._cos_l(a, b, c), self._cos_l(b, c, a), self._cos_l(c, a, b)

    def _center(self, pa, pb, pc, ga, gb, gc):
        ct = []
        for n in pa:
            ct.append(n * ga)
        for i, n in enumerate(pb):
            ct[i] += n * gb
        for i, n in enumerate(pc):
            ct[i] += n * gc
        c = []
        for k in ct:
            c.append(k / (ga + gb + gc))
        return c

    def _circumcenter(self, pa, pb, pc):
        a, b, c = self._tri(pa, pb, pc)
        center_ = self._center(
            pa,
            pb,
            pc,
            self._sin_l(a, b, c) * self._cos_l(a, b, c),
            self._sin_l(b, c, a) * self._cos_l(b, c, a),
            self._sin_l(c, a, b) * self._cos_l(c, a, b),
        )
        return center_

    def make_map(self):
        """
        foliumを利用した地図を作成し、出力する
        """
        # 地図の初期値として、新宿駅を指定
        Sinjuku = self.station_data[self.station_data["station_name"] == "新宿"].iloc[0]
        Sinjuku_location = [Sinjuku["station_lat"], Sinjuku["station_lon"]]

        # マーカーを置いていく
        # 入力地点にマーカーを置く
        m = folium.Map(location=Sinjuku_location, tiles="OpenStreetMap", zoom_start=10)
        for i in range(len(self.input_location_df)):
            # 緯度経度のリストを作成する
            location = list(self.input_location_df.iloc[i, :])
            # 地図を作る
            marker = folium.Marker(
                location=location,
                popup="Input:" + self.input_station_name[i],
                icon=folium.Icon(color="orange"),
            )

            m.add_child(marker)

        # 中心地点にマーカーを置く
        marker = folium.Marker(
            location=self.center_station_location,
            popup="Center:" + self.center_station_name,
            icon=folium.Icon(color="red"),
        )
        m.add_child(marker)
        folium_static(m)


"""
# ここから、料金ベースでの中心を求める。

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
"""

