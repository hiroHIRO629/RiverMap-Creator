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

r_type = "c"
cola = "W05_001"
colb = "W05_002"

cdir = "../csv/class_b.csv"
df = pd.read_csv(cdir,index_col=0)

#r_name = input("河川名を入力して下さい：")
r_name = "奥川"

river_info = df.loc[r_name]
print(river_info)
r_code = river_info["河川コード"]

if isinstance(r_code, np.integer):
    str_code = str(r_code)
elif len(r_code) >= 2:
    r_code = input("河川コードを入力して下さい：")
    #r_code = ""
    print("河川読み込み中!")
    str_code = str(r_code)

print(str_code[0:6],str_code)

gdf = gpd.read_file("../riverline/all_river/all_river.shp")
filtered_wsystem = gdf[gdf[cola] == str_code[0:6]]
filtered_gdf = gdf[gdf[colb] == str_code]

river_bounds = filtered_wsystem.total_bounds  # xmin, ymin, xmax, ymax
p_x = (river_bounds[2]-river_bounds[0])*0.7
m_x = (river_bounds[2]-river_bounds[0])*0.1
p_y = (river_bounds[3]-river_bounds[1])*0.1
a_y = (river_bounds[3]-river_bounds[1])*2
# 地図の範囲を河道の範囲に基づいて設定
riv_ran = [river_bounds[0]-0.03, river_bounds[2]+0.2, river_bounds[1]-0.05, river_bounds[3]+0.05]
#riv_ran = [river_bounds[0]-m_x, river_bounds[2]+p_x, river_bounds[1]-p_y, river_bounds[3]+p_y]
riv_area = [river_bounds[0]-1.2, river_bounds[2]+1.2, river_bounds[1]-1.2, river_bounds[3]+1.2]
#riv_area = [river_bounds[0]- ((p_x + m_x)/2*15), river_bounds[2]+((p_x + m_x)/2*15), river_bounds[1]-1, river_bounds[3]+1]
print("river_bounds:", river_bounds)
print("riv_ran:", riv_ran)

print("Drowing a map now!")
fig = pygmt.Figure()
grid = pygmt.datasets.load_earth_relief(resolution="03s", region=riv_ran)
fig.coast(water='skyblue', land="lightgreen", shorelines="1/0.1p", borders="1")
pygmt.makecpt(cmap="geo", series=[-500, 2000])
fig.grdimage(grid=grid, 
             projection="M15c", 
             frame=['WSne', 'xaf', 'yaf'])
fig.colorbar(frame=["a500f100", "x+lElevation", "y+lm"])
fig.coast(shorelines="1/0.1p", borders="1")

print("Drowing a riverline now! Please wait a moment.")

start_time = time.time()
total_lines = len(filtered_wsystem)
for i , line in enumerate(filtered_wsystem.geometry,1):
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
print("水系完了！")

start_time = time.time()
total_lines = len(filtered_gdf)
for i ,line in enumerate(filtered_gdf.geometry,1):
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
print("河道完了！")
#fig.plot(x=lon, y=lat, style="x0.8c", pen="1.5p,red")

# 地図上のスケールと挿入図
fig.basemap(map_scale="jBL+w10k+f+lkm+o0.5c/1c")

print("Saving a map now!")
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

fig.savefig(f"../map/{r_name}"+f"_{r_code}.png")