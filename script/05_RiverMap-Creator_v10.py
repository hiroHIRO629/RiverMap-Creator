import geopandas as gpd
import pandas as pd
import pygmt
import os
import warnings
import numpy as np
import re
import time 
import sys

os.environ['GMT_VERBOSE'] = 'q'
warnings.filterwarnings("ignore", category=UserWarning, module="pygmt")

cdir = "../csv/"
cpass = "../csv/class_b.csv"
rpass = "../riverline/all_river/all_river.shp"

r_type = input("描画するのは　a 水系？　b 河川？ c 水系と河川？（ a b c を入力)：")
print("ーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーー")

if r_type == "a":
    cola = "W05_001"
    df = pd.read_csv(cdir+f"class_{r_type}.csv",index_col=0)
elif r_type == "b":
    colb = "W05_002"
    df = pd.read_csv(cdir+f"class_{r_type}.csv",index_col=0)
else:    
    cola = "W05_001"
    colb = "W05_002"
    df = pd.read_csv(cpass,index_col=0)

if r_type == "a":
    r_name = input("水系名を入力して下さい：")
    print("ーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーー")
elif r_type == "b":
    r_name = input("河川名を入力して下さい：")
    print("ーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーー")
else:
    r_name = input("河川名を入力して下さい：")
    print("ーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーー")

river_info = df.loc[r_name]
print(river_info)
print("ーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーー")
r_code = river_info["河川コード"]

if isinstance(r_code, np.integer):
    str_code = str(r_code)
    #print("ーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーー")
    print("河川読み込み中... loading...")
elif len(r_code) >= 2:
    r_code = input("河川コードを入力して下さい：")
    print("ーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーー")
    print("河川読み込み中... loading...")
    str_code = str(r_code)

gdf = gpd.read_file(rpass)
if r_type == "a":
    filtered_gdf = gdf[gdf[cola] == str_code[0:6]]
elif r_type == "b":
    filtered_gdf = gdf[gdf[colb] == str_code]
else:
    filtered_wsystem = gdf[gdf[cola] == str_code[0:6]]
    filtered_gdf = gdf[gdf[colb] == str_code]
"""
# 河道の範囲（bounding box）を取得
if r_type == "a":
    river_bounds = filtered_gdf.total_bounds  # xmin, ymin, xmax, ymax
    p_x = (river_bounds[2]-river_bounds[0])*0.7
    m_x = (river_bounds[2]-river_bounds[0])*0.1
    p_y = (river_bounds[3]-river_bounds[1])*0.15
    riv_ran = [river_bounds[0]-m_x, river_bounds[2]+p_x, river_bounds[1]-p_y, river_bounds[3]+p_y]
    riv_area = [river_bounds[0]-1.2, river_bounds[2]+1.2, river_bounds[1]-1.2, river_bounds[3]+1.2]
elif r_type == "b":
    river_bounds = filtered_gdf.total_bounds  # xmin, ymin, xmax, ymax
    riv_ran = [river_bounds[0]-0.03, river_bounds[2]+0.17, river_bounds[1]-0.05, river_bounds[3]+0.05]
    riv_area = [river_bounds[0]-1.2, river_bounds[2]+1.2, river_bounds[1]-1.2, river_bounds[3]+1.2]
else:
    river_bounds = filtered_wsystem.total_bounds  # xmin, ymin, xmax, ymax
    p_x = (river_bounds[2]-river_bounds[0])*0.7
    m_x = (river_bounds[2]-river_bounds[0])*0.1
    p_y = (river_bounds[3]-river_bounds[1])*0.15
    riv_ran = [river_bounds[0]-m_x, river_bounds[2]+p_x, river_bounds[1]-p_y, river_bounds[3]+p_y]
    riv_area = [river_bounds[0]-1.2, river_bounds[2]+1.2, river_bounds[1]-1.2, river_bounds[3]+1.2]
"""
if r_type == "a":
    river_bounds = filtered_gdf.total_bounds  # xmin, ymin, xmax, ymax
elif r_type == "b":
    river_bounds = filtered_gdf.total_bounds  # xmin, ymin, xmax, ymax
else:
    river_bounds = filtered_wsystem.total_bounds  # xmin, ymin, xmax, ymax

p_x = (river_bounds[2]-river_bounds[0])*0.7
m_x = (river_bounds[2]-river_bounds[0])*0.1
p_y = (river_bounds[3]-river_bounds[1])*0.15
riv_ran = [river_bounds[0]-m_x, river_bounds[2]+p_x, river_bounds[1]-p_y, river_bounds[3]+p_y]
if (riv_ran[3]-riv_ran[2]) <= 0.1:
    riv_ran = [river_bounds[0]-0.03, river_bounds[2]+0.17, river_bounds[1]-0.05, river_bounds[3]+0.05]
else:
    riv_ran = riv_ran
riv_area = [river_bounds[0]-1.2, river_bounds[2]+1.2, river_bounds[1]-1.2, river_bounds[3]+1.2]

print("river_bounds:", river_bounds)
print("河川描画中! Drowing a riverline now!")

fig = pygmt.Figure()
grid = pygmt.datasets.load_earth_relief(resolution="03s", region=riv_ran)
fig.coast(water='skyblue', land="lightgreen", shorelines="1/0.1p", borders="1")
pygmt.makecpt(cmap="geo", series=[-500, 2000])
fig.grdimage(grid=grid, 
             projection="M15c", 
             frame=['WSne', 'xaf', 'yaf'])
fig.colorbar(frame=["a500f100", "x+lElevation", "y+lm"])
fig.coast(shorelines="1/0.1p", borders="1")

if r_type == "a":
    start_time = time.time()
    total_lines = len(filtered_gdf)
    for i, line in enumerate(filtered_gdf.geometry,1):
        if line.geom_type == 'LineString':
            x, y = line.xy
            fig.plot(x=x, y=y, pen="0.7p,blue")
        elif line.geom_type == 'MultiLineString':
            for ls in line:
                x, y = ls.xy
                fig.plot(x=x, y=y, pen="0.7p,blue")
        elapsed_time = time.time() - start_time
        progress = i / total_lines * 100
        sys.stdout.write(f"\r進捗度: {progress:.2f}% | 経過時間: {elapsed_time:.2f} 秒")
        sys.stdout.flush()

elif r_type == "b":
    start_time = time.time()
    total_lines = len(filtered_gdf)
    for i, line in enumerate(filtered_gdf.geometry,1):
        if line.geom_type == 'LineString':
            x, y = line.xy
            fig.plot(x=x, y=y, pen="0.7p,blue")
        elif line.geom_type == 'MultiLineString':
            for ls in line:
                x, y = ls.xy
                fig.plot(x=x, y=y, pen="0.7p,blue")
        elapsed_time = time.time() - start_time
        progress = i / total_lines * 100
        sys.stdout.write(f"\r進捗度: {progress:.2f}% | 経過時間: {elapsed_time:.2f} 秒")
        sys.stdout.flush()

else:
    start_time = time.time()
    total_lines = len(filtered_wsystem)
    for i, line in enumerate(filtered_wsystem.geometry,1):
        if line.geom_type == 'LineString':
            x, y = line.xy
            fig.plot(x=x, y=y, pen="0.7p,blue")
        elif line.geom_type == 'MultiLineString':
            for ls in line:
                x, y = ls.xy
                fig.plot(x=x, y=y, pen="0.7p,blue")
        elapsed_time = time.time() - start_time
        progress = i / total_lines * 100
        sys.stdout.write(f"\r進捗度: {progress:.2f}% | 経過時間: {elapsed_time:.2f} 秒")
        sys.stdout.flush()

    start_time = time.time()
    total_lines = len(filtered_gdf)
    for i , line in enumerate(filtered_gdf.geometry,1):
        if line.geom_type == 'LineString':
            x, y = line.xy
            fig.plot(x=x, y=y, pen="1.2p,red")
        elif line.geom_type == 'MultiLineString':
            for ls in line:
                x, y = ls.xy
                fig.plot(x=x, y=y, pen="1.2p,red")
        elapsed_time = time.time() - start_time
        progress = i / total_lines * 100
        sys.stdout.write(f"\r進捗度: {progress:.2f}% | 経過時間: {elapsed_time:.2f} 秒")
        sys.stdout.flush()

#fig.plot(x=lon, y=lat, style="x0.8c", pen="1.5p,red")

if (riv_ran[1]-riv_ran[0]) <= 0.099:
    fig.basemap(map_scale="jBL+w2k+f+lkm+o0.5c/1c")
elif (riv_ran[1]-riv_ran[0]) >= 1.0:
     fig.basemap(map_scale="jBL+w50k+f+lkm+o0.5c/1c")
else:
    fig.basemap(map_scale="jBL+w10k+f+lkm+o0.5c/1c")

with fig.inset(
    position="jTR+o0.1c",
    box="+gwhite+p1p",
    region=riv_area,  
    projection="M5c",
):   
    fig.coast(
        dcw="JP+glightbrown+p0.2p",
        area_thresh=10000,
        rivers="a/0.8p,white,solid",
    )
    rectangle = [[riv_ran[0], riv_ran[2], riv_ran[1], riv_ran[3]]]
    fig.plot(data=rectangle, style="r+s", pen="1.5p,red")

fig.savefig(f"../map/{r_name}_{r_code}_{r_type}.png")
print("画像保存完了! mission complete!")