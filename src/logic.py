# とりあえず距離ベースで考える。
##関東三県に対応

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import functions as func
import streamlit as st

from streamlit_folium import folium_static
import folium


class central_station:
    def __init__(self, station_data, input_station_name):
        self.station_data = station_data
        self.input_station_name = input_station_name

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
        st.write(self.input_location_df)

        ##料金データ（csv）を読み込む
        self.fare_df = pd.read_csv(
            "./data/fare/fare_all.csv", encoding="shift jis", index_col="Unnamed: 0"
        )

    def calc_center_location_base(self):
        """
        駅名を入力し、中心の座標とそこから近い駅（の名前と座標）を出力する関数
        距離ベースで計算を行う。具体的には、n = 3の時は外心（全員の移動距離が同じ）
        n != 3の時は重心とする。
        
        Returns
            Station_name：入力した駅名
            Input_location：入力した駅の緯度経度（リストのリスト）
            Center_location：中心地点の緯度経度（リスト）
            Ceneter_station_name：中心地点から近い駅名
            Center_station_location：中心地点から近い駅の緯度経度（リスト）
        """
        n = len(self.input_station_name)

        # 中心の緯度経度を求める
        # n = 3の時は外心を求める。
        if n == 3:
            center_location_list = self._circumcenter(
                list(self.input_location_df.iloc[0, :]),
                list(self.input_location_df.iloc[1, :]),
                list(self.input_location_df.iloc[2, :]),
            )
        # n ≠ 3の時は重心を求める
        else:
            center_location_list = np.average(self.input_location_list, axis=0)

        # st.write(center_location_list)
        # st.write(self.station_data["station_lat"])
        # st.write(self.station_data["station_lon"])

        # 中心から最も近い駅を求める
        min_index = np.argmin(
            (self.station_data["station_lat"] - center_location_list[0]) ** 2
            + (self.station_data["station_lon"] - center_location_list[1]) ** 2
        )
        center_station = self.station_data.iloc[min_index]
        center_station_name = center_station["station_name"]

        center_station_ido = center_station["station_lat"]
        center_station_keido = center_station["station_lon"]
        center_station_location = [center_station_ido, center_station_keido]

        return (
            center_station_name,
            center_station_location,
        )

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


def make_map(
    station_data,
    input_station_name_list,
    input_location_df,
    center_station_name,
    center_station_location,
):
    """
    foliumを利用した地図を作成し、出力する

    Augs
        station_data:駅のデータ(df)
        input_station_nake_list:入力駅名
        input_location_list:入力駅の緯度経度
        center_station_name:中心駅名
        center_station_location:中心駅の緯度経度
    """
    # 地図の初期値として、新宿駅を指定
    Sinjuku = station_data[station_data["station_name"] == "新宿"].iloc[0]
    Sinjuku_location = [Sinjuku["station_lat"], Sinjuku["station_lon"]]

    # マーカーを置いていく
    # 入力地点にマーカーを置く
    m = folium.Map(location=Sinjuku_location, tiles="OpenStreetMap", zoom_start=13)
    for i in range(len(input_location_df)):
        # 緯度経度のリストを作成する
        location = list(input_location_df.iloc[i, :])
        # 地図を作る
        marker = folium.Marker(
            location=location,
            popup="Input:" + input_station_name_list[i],
            icon=folium.Icon(color="orange"),
        )

        m.add_child(marker)

    # 中心地点にマーカーを置く
    marker = folium.Marker(
        location=center_station_location,
        popup="Center:" + center_station_name,
        icon=folium.Icon(color="red"),
    )
    m.add_child(marker)
    folium_static(m)
