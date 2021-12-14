#諸々の関数を定義
import numpy as np
import pandas as pd
import math
from matplotlib import pyplot as plt
import folium


#三角形の外心を求めるための諸々の関数（from：https://ictsr4.com/sw/python-2/#index_id3）

#1 2つの長さを求める
def length(p1,p2):
    s=0
    for i,j in zip(p1,p2):
        s+=(i-j)**2
    return s**0.5    

#2 三角形の3つの座標から3辺の長さを求める
def tri(pa,pb,pc):
    a=length(pc,pb)
    b=length(pa,pc)
    c=length(pa,pb)
    return a,b,c

#3 三角形の3つの座標からヘロンの公式を使い面積を求める
def square(a,b,c):
        s=(a+b+c)/2
        return (s*(s-a)*(s-b)*(s-c))**0.5

#4 三角形の3つの長さから、1番目の引数の角のsinの値を求める    
def sin_l(a,b,c):
    s=square(a,b,c)
    return(s*2/b/c)

#5 三角形の3つの長さから、1番目の引数の角のcosの値を求める    
def cos_l(a,b,c):
    return(b**2+c**2-a**2)/(2*b*c)

#6 原点から2つの点となす角のsinの値を求める    
def sin_v(p1,p2):
    a,b,c=tri((0,0),p1,p2)
    return sin_l(a,b,c)

#7 原点から2つの点となす角のcosの値を求める    
def cos_v(p1,p2):
    a,b,c=tri((0,0),p1,p2)
    return cos_l(a,b,c)

#8 三角形の3つの座標から3つの角のsinの値を求める
def sin_t(pa,pb,pc):
    a,b,c=tri(pa,pb,pc)
    s=square(a,b,c)
    return s*2/b/c,s*2/c/a,s*2/a/b

#9 三角形の3つの座標から3つの角のcosの値を求める
def cos_t(pa,pb,pc):
    a,b,c=tri(pa,pb,pc)
    return cos_l(a,b,c),cos_l(b,c,a),cos_l(c,a,b)

def center(pa,pb,pc,ga,gb,gc):
    ct=[]
    for n in pa:
        ct.append(n*ga)            
    for i,n in enumerate(pb):
        ct[i]+=n*gb            
    for i,n in enumerate(pc):
        ct[i]+=n*gc
    c=[]    
    for k in ct:
        c.append(k/(ga+gb+gc))        
    return c

def circumcenter(pa,pb,pc):
    a,b,c=tri(pa,pb,pc)
    center_ = center(pa,pb,pc,
                  sin_l(a,b,c)*cos_l(a,b,c),
                  sin_l(b,c,a)*cos_l(b,c,a),
                  sin_l(c,a,b)*cos_l(c,a,b))
    return center_

def input_station_name(station_data):
    print("人数は")
    n = int(input())

    #駅名を入力する
    ##可能性のある駅データのリストを持ってくる
    Station_name_data = list(station_data["station_name"])
    ##駅名を保存していく
    Station_name = []
    for i in range(n):
        print(i + 1, "人目の駅は？:")
        name = input()
        
        #データ上に駅名が存在しないのならば、名前を入れなおす
        while not (name in Station_name_data):
            print("駅名が存在しません。もう一度入力してください。")
            name = input()
            
        #データ上に駅名が存在している
        Station_name.append(name)

    return Station_name

# 駅名を入力し、中心の座標とそこから近い駅（の名前と座標）を出力する関数
# 距離ベースで計算を行う。具体的には、n = 3の時は外心（全員の移動距離が同じ）
# n != 3の時は重心とする。
def calc_center(Station_name, station_data):    
    n = len(Station_name)
    #駅名を検索して、緯度と経度を取得
    Input_location = []
    Ido = []
    Keido = []
    for name in Station_name:
        each_station = station_data[station_data["station_name"] == name]
        ido = np.array(each_station["station_lat"])
        keido = np.array(each_station["station_lon"])
        
        Input_location.append([ido[0], keido[0]]) 
        Ido.append(ido[0])
        Keido.append(keido[0])

    #n = 3の時は外心を求める。
    if n == 3:
        Center_location = circumcenter((Ido[0], Keido[0]), (Ido[1], Keido[1]), (Ido[2], Keido[2]))
    #n ≠ 3の時は重心を求める
    else:
        Center_location = [sum(Ido) / n, sum(Keido) / n]
    
    #中心から最も近い駅を求める
    min_index = np.argmin((station_data["station_lat"] - Center_location[0]) ** 2 + (station_data["station_lon"] - Center_location[1]) ** 2)
    Center_station = station_data.iloc[min_index]
    Center_station_name = Center_station["station_name"]
    Center_station_ido = Center_station["station_lat"]
    Center_station_keido = Center_station["station_lon"]
    Center_station_location = [Center_station_ido, Center_station_keido]

    #出力：
    ##Station_name：入力した駅名
    ##Input_location：入力した駅の緯度経度（リストのリスト）
    ##Center_location：中心地点の緯度経度（リスト）
    ##Ceneter_station_name：中心地点から近い駅名
    ##Center_station_location：中心地点から近い駅の緯度経度（リスト）
    return Station_name, Input_location, Center_location, Center_station_name, Center_station_location


#料金ベースで最適な駅を考える。料金の合計値を最小にするような駅を考える。
#入力：
## Station_name：検索したい駅名のリスト
## station_data：駅の名前と緯度経度のデータ
## Fare：料金データ
def calc_center_fare_sum(Station_name, station_data, Fare):
    n = len(Station_name)
    
    #駅名を検索して、緯度と経度を取得
    Input_location = []
    Ido = []
    Keido = []
    for name in Station_name:
        each_station = station_data[station_data["station_name"] == name]
        ido = np.array(each_station["station_lat"])
        keido = np.array(each_station["station_lon"])
        
        Input_location.append([ido[0], keido[0]]) 
        Ido.append(ido[0])
        Keido.append(keido[0])

    #全員の料金の合計値が最小となるような駅を検索する。
    Sum_of_fare = []
    
    # 全ての駅名リストを持ってくる
    All_station_name = list(station_data["station_name"])

    for name in All_station_name: ##全ての駅名でiterate
        ##全員の料金の合計値を計算する。
        sum_of_fare = 0
        for input_name in Station_name:
            sum_of_fare += (Fare[name][input_name])

        #print(name, sum_of_fare)
        ##料金の合計値を格納
        Sum_of_fare.append(sum_of_fare)
    
    ##料金の合計値を最小化するような駅を検索する
    min_of_sum = min(Sum_of_fare)
    min_index = Sum_of_fare.index(min_of_sum)
        
    #中心から最も近い駅を求める
    Center_station = station_data.iloc[min_index]
    Center_station_name = Center_station["station_name"]
    Center_station_ido = Center_station["station_lat"]
    Center_station_keido = Center_station["station_lon"]
    Center_station_location = [Center_station_ido, Center_station_keido]

    #出力：
    ##Station_name：入力した駅名
    ##Input_location：入力した駅の緯度経度（リストのリスト）
    ##Ceneter_station_name：中心地点から近い駅名
    ##Center_station_location：中心地点から近い駅の緯度経度（リスト）
    return Station_name, Input_location, Center_station_name, Center_station_location, min_of_sum


#料金ベースで最適な駅を考える。ここでは、料金の最大値を最小にするような駅を考える。
def calc_center_fare_min(Station_name, station_data, Fare):
    n = len(Station_name)
    
    #駅名を検索して、緯度と経度を取得
    Input_location = []
    Ido = []
    Keido = []
    for name in Station_name:
        each_station = station_data[station_data["station_name"] == name]
        ido = np.array(each_station["station_lat"])
        keido = np.array(each_station["station_lon"])
        
        Input_location.append([ido[0], keido[0]]) 
        Ido.append(ido[0])
        Keido.append(keido[0])
    
    #全員の料金の合計値が最小となるような駅を検索する。
    Max_of_fare = []
    
    # 全ての駅名リストを持ってくる
    All_station_name = list(station_data["station_name"])

    for name in All_station_name: ##全ての駅名でiterate
        ##全員の料金の中で、最大値を計算する。
        max_of_fare = 0
        for input_name in Station_name:
            max_of_fare = max([max_of_fare, Fare[name][input_name]])

        #print(name, sum_of_fare)
        ##料金の最大値を格納
        Max_of_fare.append(max_of_fare)
    
    ##料金の最大値を最小化するような駅を検索する
    min_of_max = min(Max_of_fare)
    min_index = Max_of_fare.index(min_of_max)
        
    #中心から最も近い駅を求める
    Center_station = station_data.iloc[min_index]
    Center_station_name = Center_station["station_name"]
    Center_station_ido = Center_station["station_lat"]
    Center_station_keido = Center_station["station_lon"]
    Center_station_location = [Center_station_ido, Center_station_keido]

    #出力：
    ##Station_name：入力した駅名
    ##Input_location：入力した駅の緯度経度（リストのリスト）
    ##Ceneter_station_name：中心地点から近い駅名
    ##Center_station_location：中心地点から近い駅の緯度経度（リスト）
    return Station_name, Input_location, Center_station_name, Center_station_location, min_of_max


#地図を作成する関数
def make_map(station_data, Station_name, Input_location, Center_location, Center_station_name, Center_station_location):
    #地図を初期化
    ##地図の初期値として、新宿駅を指定
    Sinjuku = station_data[station_data["station_name"] == "新宿"].iloc[0]
    Sinjuku_location = [Sinjuku["station_lat"], Sinjuku["station_lon"]]

    m = folium.Map(location=Sinjuku_location,
               tiles='OpenStreetMap',
               zoom_start=13)

    #マーカーを置いていく
    ##入力地点にマーカーを置く
    for i in range(len(Input_location)):
        marker = folium.Marker(
        location = Input_location[i], 
        popup='Input:' + Station_name[i],              
        icon=folium.Icon(color='orange'))
        m.add_child(marker)

    ##中心地点にマーカーを置く
    marker = folium.Marker(
        location=Center_station_location, 
        popup= "Center:" + Center_station_name,                    
        icon=folium.Icon(color='red'))
    m.add_child(marker)
    
    return m
