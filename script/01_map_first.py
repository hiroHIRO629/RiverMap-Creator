import geopandas as gpd
import pygmt
######################################################
##############------river_list-----###################
shigenobugawa = ([132.63, 133.08, 33.65, 34.0],
             [132, 135, 32.5, 34.5], #shikoku
             '06_38','880801','shigenobugawa')
ooitagawa = ([131.25,132.0,33.02,33.5],
         [129, 133, 31, 34], #kyuusyuu
         '07_44','890919','ooitagawa')
mogamigawa = ([139.7,141,37.75,39.1],
          [138, 142, 37, 41], #tohoku
          '07_06','820211','mogamigawa')
#######################################################
#######################################################

river = shigenobugawa  # <- river_listから選ぶ
lon = 131.62 # <-　印をつけたい地点の経度
lat = 33.24 # <- -印をつけたい地点の緯度
#label = "Bentenohashi" # <- ラベル名

print("今は地図を描いてます🗾")
riv_ran = river[0] 
area = river[1]
#print(riv_ran[0])
fig = pygmt.Figure()
grid = pygmt.datasets.load_earth_relief(resolution="01s", region=riv_ran)
fig.coast(water='skyblue',land="lightgreen", shorelines="1/0.1p", borders="1")
pygmt.makecpt(cmap="geo", series=[-500, 2000])
fig.grdimage(grid=grid, 
             projection="M15c", 
             frame=['WSne', 'xaf', 'yaf'])
fig.colorbar(frame=["a500f100", "x+lElevation", "y+lm"])
fig.coast(shorelines="1/0.1p", borders="1")

print("今は河道を描いてます🂥")
gdf = gpd.read_file("../riverline/W05-" + river[2] + "_GML/W05-" + river[2] +"-g_Stream.shp") 
filtered_gdf = gdf[gdf["W05_001"] == river[3]] 
filtered_line = gdf[gdf["W05_002"] == "8808010001"]

for line in filtered_gdf.geometry:
    if line.geom_type == 'LineString':
        x, y = line.xy
        fig.plot(x=x, y=y, pen="1.3p,blue")
    elif line.geom_type == 'MultiLineString':
        for ls in line:
            x, y = ls.xy
            fig.plot(x=x, y=y, pen="1.3p,blue")

for line in filtered_line.geometry:
    if line.geom_type == 'LineString':
        x, y = line.xy
        fig.plot(x=x, y=y, pen="1.5p,red")
    elif line.geom_type == 'MultiLineString':
        for ls in line:
            x, y = ls.xy
            fig.plot(x=x, y=y, pen="1.5p,red")


#fig.plot(x=lon,y=lat,style="x0.8c",pen="1.5p,red")
##########2.---plot_list---###################
#fig.plot(x=132.7479,y=33.8132,style="x0.5c",pen="1.5p,red",label="Isite")
#fig.plot(x=132.7007,y=33.8055,style="x0.5c",pen="1.5p,black",label="Shigenobu")
#fig.plot(x=131.62,y=33.24,style="x0.8c",pen="1.5p,red",label="Bentenoohashi")
##############################################

#fig.legend(position="jTL+o0.1c",box="+gwhite")
#fig.basemap(map_scale="jBR+w10k+f+lkm+o0.5c/1c")

print("今は微調整してます🀄︎")

with fig.inset(
    position="jTR+o0.1c",
    box="+gwhite+p1p",
    region=area,
    projection="M5c",
):   
    fig.coast(
        dcw="JP+glightbrown+p0.2p",
        area_thresh=10000,
        rivers="a/0.8p,white,solid",
    )
    rectangle = [[riv_ran[0], riv_ran[2], riv_ran[1], riv_ran[3]]]
    fig.plot(data=rectangle, style="r+s", pen="1.5p,red")


#fig.savefig(f"../figure/{river[4]}.png")
fig.savefig(f"../map/{river}.png")
