import geopandas as gpd
import pygmt

######################################################
##############------river_list-----###################
#shigenobugawa = ([132.63, 133.08, 33.65, 34.0],
#                 [132, 135, 32.5, 34.5], #shikoku
#                 '06_38', '880801', 'shigenobugawa')
#ooitagawa = ([131.25, 132.0, 33.02, 33.5],
#             [129, 133, 31, 34], #kyuusyuu
#             '07_44', '890919', 'ooitagawa')
#mogamigawa = ([139.7, 141, 37.75, 39.1],
#              [138, 142, 37, 41], #tohoku
#              '07_06', '820211', 'mogamigawa')
#######################################################
#######################################################

shigenobugawa = ('06_38', '880801', 'shigenobugawa')
ooitagawa = ('07_44', '890919', 'ooitagawa')
mogamigawa = ('07_06', '820211', 'mogamigawa')

river = shigenobugawa  # <- river_listから選ぶ
lon = 131.62 # <- 印をつけたい地点の経度
lat = 33.24 # <- 印をつけたい地点の緯度

# 河道データの読み込み
gdf = gpd.read_file("../riverline/W05-" + river[0] + "_GML/W05-" + river[0] + "-g_Stream.shp") 
filtered_gdf = gdf[gdf["W05_001"] == river[1]] 

# 河道の範囲（bounding box）を取得
river_bounds = filtered_gdf.total_bounds  # xmin, ymin, xmax, ymax

# 地図の範囲を河道の範囲に基づいて設定
riv_ran = [river_bounds[0]-0.03, river_bounds[2]+0.17, river_bounds[1]-0.03, river_bounds[3]+0.03]
riv_area = [river_bounds[0]-1.5, river_bounds[2]+1.5, river_bounds[1]-1.5, river_bounds[3]+1.5]
print("今地図描いてます")
fig = pygmt.Figure()
grid = pygmt.datasets.load_earth_relief(resolution="01s", region=riv_ran)
fig.coast(water='skyblue', land="lightgreen", shorelines="1/0.1p", borders="1")
pygmt.makecpt(cmap="geo", series=[-500, 2000])
fig.grdimage(grid=grid, 
             projection="M15c", 
             frame=['WSne', 'xaf', 'yaf'])
fig.colorbar(frame=["a500f100", "x+lElevation", "y+lm"])
fig.coast(shorelines="1/0.1p", borders="1")

print("今河道描いてます")
for line in filtered_gdf.geometry:
    if line.geom_type == 'LineString':
        x, y = line.xy
        fig.plot(x=x, y=y, pen="0.7p,blue")
    elif line.geom_type == 'MultiLineString':
        for ls in line:
            x, y = ls.xy
            fig.plot(x=x, y=y, pen="0.7p,blue")

fig.plot(x=lon, y=lat, style="x0.8c", pen="1.5p,red")

# 地図上のスケールと挿入図
fig.basemap(map_scale="jBR+w10k+f+lkm+o0.5c/1c")

print("今微調整してます")
with fig.inset(
    position="jTR+o0.1c",
    box="+gwhite+p1p",
    region=riv_area,  # 大きい範囲を表示
    projection="M5c",
):   
    fig.coast(
        dcw="JP+glightbrown+p0.2p",
        area_thresh=10000,
        rivers="a/0.8p,white,solid",
    )
    rectangle = [[riv_ran[0], riv_ran[2], riv_ran[1], riv_ran[3]]]
    fig.plot(data=rectangle, style="r+s", pen="1.5p,red")

fig.savefig("../map/test.png")
