import geopandas as gpd
import pandas as pd
import pygmt
import os
import warnings
import numpy as np
import time
import sys

os.environ['GMT_VERBOSE'] = 'q'
warnings.filterwarnings("ignore", category=UserWarning, module="pygmt") #警告無視

def get_user_input(prompt, options=None):
    while True:
        user_input = input(prompt).strip()
        if options is None or user_input in options:
            return user_input
        print(f"無効な値です． {options} から選択しろ！．")

def load_river_data(r_type):
    col = "W05_001" if r_type == "a" else "W05_002"
    cdir = f"../csv/class_{r_type}.csv"
    return pd.read_csv(cdir, index_col=0), col

def get_river_code(df, r_name):
    if r_name not in df.index:
        print(f" '{r_name}' は存在しません．正確に入力しろ！．")
        return None
    
    river_info = df.loc[r_name]
    print(river_info)
    
    r_code = river_info['河川コード']
    if isinstance(r_code, np.integer):
        return str(r_code)
    elif len(r_code) >= 2:
        print("ーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーー")
        return get_user_input("河川コードを入力して下さい：")
    else:
        return r_code

def load_and_filter_gdf(col, str_code):
    gdf = gpd.read_file("../riverline/all_river/all_river.shp")
    return gdf[gdf[col] == str_code]


def create_map(filtered_gdf, r_name, str_code, resolution):
    river_bounds = filtered_gdf.total_bounds #minx, miny, maxx, maxy
    #p_x = (river_bounds[2]-river_bounds[0])*0.3
    #m_x = (river_bounds[2]-river_bounds[0])*0.1
    #p_m_y = ((river_bounds[2]-river_bounds[0]) + p_x + m_x )/ 2
    riv_ran = [river_bounds[0]-0.03, river_bounds[2]+0.2, river_bounds[1]-0.03, river_bounds[3]+0.03]
    #riv_ran = [river_bounds[0]-m_x, river_bounds[2]+p_x, river_bounds[1]-p_m_y, river_bounds[3]+p_m_y]
    riv_area = [river_bounds[0]-1.5, river_bounds[2]+1.5, river_bounds[1]-1.5, river_bounds[3]+1.5]

    print("標高図を作成中！🗾")
    fig = pygmt.Figure()
    #fig.basemap(region=riv_ran,projection="M15c",frame=['WSne', 'xaf', 'yaf'])
    grid = pygmt.datasets.load_earth_relief(resolution=resolution, region=riv_ran)
    fig.coast(water='skyblue', land="lightgreen", shorelines="1/0.1p", borders="1")
    pygmt.makecpt(cmap="geo", series=[-500, 2000])
    fig.grdimage(grid=grid, projection="M15c", frame=['WSne', 'xaf', 'yaf']) 
    fig.colorbar(frame=["a500f100", "x+lElevation", "y+lm"])
    fig.coast(shorelines="1/0.1p", borders="1")

    print("河道を描画中！")
    start_time = time.time()
    total_lines = len(filtered_gdf)
    
    for i, line in enumerate(filtered_gdf.geometry, 1):
        if line.geom_type == 'LineString':
            x, y = line.xy
            fig.plot(x=x, y=y, pen="0.7p,blue")
        elif line.geom_type == 'MultiLineString':
            for ls in line:
                x, y = ls.xy
                fig.plot(x=x, y=y, pen="0.7p,blue")
        
        # 経過時間の計算と表示
        elapsed_time = time.time() - start_time
        progress = i / total_lines * 100
        sys.stdout.write(f"\r進捗度: {progress:.2f}% | 経過時間: {elapsed_time:.2f} 秒")
        sys.stdout.flush()

    print("\n河道描画完了！")

    fig.basemap(map_scale="jBL+w10k+f+lkm+o0.5c/1c")

    #fig.plot(x=132.545,y=33.508,style="x0.8c",pen="1.5p,red",label="hijikawabashi")
    #fig.plot(x=137.0138,y=36.7659,style="x0.8c",pen="1.5p,red",label="hutakamibashi")
    #fig.plot(x=132.736,y=33.8054,style="x0.8c",pen="1.5p,red",label="jitensya")
    #fig.plot(x=131.62,y=33.24,style="x0.8c",pen="1.5p,red",label="Bentenoohashi")

    with fig.inset(position="jTR+o0.1c", box="+gwhite+p1p", region=riv_area, projection="M5c"):   
        fig.coast(dcw="JP+glightbrown+p0.2p", area_thresh=10000, rivers="a/0.8p,white,solid")
        rectangle = [[riv_ran[0], riv_ran[2], riv_ran[1], riv_ran[3]]]
        fig.plot(data=rectangle, style="r+s", pen="1.5p,red")
        
    print("画像保存完了！　mission complete!!")
    fig.savefig(f"../fig2/{r_name}_{str_code}.png")


def main():
    print("ーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーー")
    r_type = get_user_input("描画するのは　a 水系？ b 河川？　( a か b を入力 )：", options=['a', 'b'])
    df, col = load_river_data(r_type)
    print("ーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーー")
    r_name = get_user_input("河川名を入力して下さい：")
    print("ーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーー")
    #resolution = get_user_input("解像度を入力して下さい．（01s，03s，15s を入力）：", options=['01s', '03s', '15s'])
    resolution = "01s"
    print("ーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーー")
    str_code = get_river_code(df, r_name)
    print("ーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーー")
    print("河川読み込み中！🔍 loading...")
    if str_code is None:
        return
    
    #print(f"河川コードは {str_code} です")
    filtered_gdf = load_and_filter_gdf(col, str_code)
    
    if filtered_gdf.empty:
        print(f"No data found for river code {str_code}")
        return
    
    create_map(filtered_gdf, r_name, str_code, resolution)

if __name__ == "__main__":
    main()
