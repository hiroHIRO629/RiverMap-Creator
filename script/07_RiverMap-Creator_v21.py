import streamlit as st
import geopandas as gpd
import pandas as pd
import pygmt
import os
import warnings
import numpy as np
import io
import tempfile
#from module import plot_x

# Suppress warnings
os.environ['GMT_VERBOSE'] = 'q'
warnings.filterwarnings("ignore", category=UserWarning, module="pygmt")

# Constants
CSV_DIR = "../csv/"
CLASS_B_CSV = os.path.join(CSV_DIR, "class_b.csv")
RIVER_SHAPEFILE = "../riverline/all_river/all_river.shp"
HORIZONTAL_LOGO = "../img/RMC_long.png"
ICON_LOGO = "../img/RMC.png"
A_PASS = "../img/a.png"
B_PASS = "../img/b.png"
C_PASS = "../img/c.png"
MAP_TYPES = {"a": "水系全体", "b": "河川", "c": "水系全体と河川"}
POINT_OPTIONS = {"a": "目印を描画", "b": "目印を描画しない"}

@st.cache_data
def load_river_data(r_type):
    if r_type in ["a", "b"]:
        return pd.read_csv(os.path.join(CSV_DIR, f"class_{r_type}.csv"), index_col=0)
    elif r_type == "c":
        return pd.read_csv(CLASS_B_CSV, index_col=0)
    else:
        raise ValueError("Invalid river type selected.")

@st.cache_data
def load_river_shapefile():
    return gpd.read_file(RIVER_SHAPEFILE)

def filter_gdf(_gdf, r_type, str_code):
    if r_type == "a":
        return _gdf[_gdf["W05_001"] == str_code[:6]]
    elif r_type == "b":
        return _gdf[_gdf["W05_002"] == str_code]
    elif r_type == "c":
        filtered_wsystem = _gdf[_gdf["W05_001"] == str_code[:6]]
        filtered_river = _gdf[_gdf["W05_002"] == str_code]
        return filtered_wsystem, filtered_river
    else:
        raise ValueError("Invalid river type for filtering.")

def calculate_map_bounds(bounds):
    x_padding = (bounds[2] - bounds[0]) * 0.1
    y_padding = (bounds[3] - bounds[1]) * 0.15
    
    riv_ran = [
        bounds[0] - x_padding,
        bounds[2] + (bounds[2] - bounds[0]) * 0.7,
        bounds[1] - y_padding,
        bounds[3] + y_padding
    ]
    
    if (riv_ran[3] - riv_ran[2]) <= 0.2:
        riv_ran = [bounds[0] - 0.03, bounds[2] + 0.17, bounds[1] - 0.05, bounds[3] + 0.05]
    
    riv_area = [bounds[0] - 1.2, bounds[2] + 1.2, bounds[1] - 1.2, bounds[3] + 1.2]
    
    return riv_ran, riv_area

def plot_river_lines(fig, gdf, pen_style, progress_bar):
    total_lines = len(gdf)
    for i, line in enumerate(gdf.geometry, 1):
        if line.geom_type == 'LineString':
            x, y = line.xy
            fig.plot(x=x, y=y, pen=pen_style)
        elif line.geom_type == 'MultiLineString':
            for ls in line:
                x, y = ls.xy
                fig.plot(x=x, y=y, pen=pen_style)
        progress_bar.progress(i / total_lines)

def create_map(r_type, r_code, p_type, lon, lat):
    # スピナー内のカスタムメッセージ
    with st.spinner("河川データを読み込み中... 約20秒お待ちください。"):
        gdf = load_river_shapefile()
        filtered_data = filter_gdf(gdf, r_type, str(r_code))

        if r_type == "c":
            filtered_wsystem, filtered_gdf = filtered_data
            bounds = filtered_wsystem.total_bounds
        else:
            filtered_gdf = filtered_data
            bounds = filtered_gdf.total_bounds

        riv_ran, riv_area = calculate_map_bounds(bounds)

    st.success("河川データの読み込みが完了しました！ completed loading!")

    # 作図
    fig = pygmt.Figure()
    grid = pygmt.datasets.load_earth_relief(resolution="03s", region=riv_ran)
    fig.coast(water='skyblue', land="lightgreen", shorelines="1/0.1p", borders="1")
    pygmt.makecpt(cmap="geo", series=[-500, 2000])
    fig.grdimage(grid=grid, projection="M15c", frame=['WSne', 'xaf', 'yaf'])
    fig.colorbar(frame=["a500f100", "x+lElevation", "y+lm"])
    fig.coast(shorelines="1/0.1p", borders="1")

    progress_bar = st.progress(0)
    if r_type in ["a", "b"]:
        plot_river_lines(fig, filtered_gdf, "0.7p,blue", progress_bar)
    elif r_type == "c":
        plot_river_lines(fig, filtered_wsystem, "0.7p,blue", progress_bar)
        plot_river_lines(fig, filtered_gdf, "1.2p,red", progress_bar)
    progress_bar.empty()

    # スケールとインセットマップの追加
    scale_width = "2k" if (riv_ran[1]-riv_ran[0]) <= 0.099 else "50k" if (riv_ran[1]-riv_ran[0]) >= 1.0 else "10k"
    fig.basemap(map_scale=f"jBL+w{scale_width}+f+lkm+o0.5c/1c")

    with fig.inset(position="jTR+o0.1c", box="+gwhite+p1p", region=riv_area, projection="M5c"):
        fig.coast(dcw="JP+glightbrown+p0.2p", area_thresh=10000, rivers="a/0.8p,white,solid")
        rectangle = [[riv_ran[0], riv_ran[2], riv_ran[1], riv_ran[3]]]
        fig.plot(data=rectangle, style="r+s", pen="1.5p,red")

    if p_type == "a":
        fig.plot(x=lon, y=lat, style="x0.8c", pen="1.5p,red")

    return fig

def main():
    st.markdown('<p style="font-family:optima; color:dodgerblue; font-size:70px;">RiverMap-Creator</p>', unsafe_allow_html=True)
    st.subheader("国内の対象河川を中心とした地図を自動作成", divider='grey')
    st.logo(HORIZONTAL_LOGO, size = "large", icon_image=ICON_LOGO)
    st.sidebar.markdown("## Welcome!!")
    st.sidebar.markdown("・国内河川対象の地図作成アプリ")
    st.sidebar.markdown("・作成された画像はダウンロード可能")
    st.sidebar.markdown("(※大河川は作図に20分程度かかります)")
    
    st.write("作図できる地図の種類は以下の3つ")
    col1, col2, col3 = st.columns(3,vertical_alignment="bottom")
    with col1:
        st.write("a 水系全体")
        st.image(A_PASS)
    with col2:
        st.write("b 河川")
        st.image(B_PASS)
    with col3:
        st.write("c 水系全体と河川")
        st.image(C_PASS)
    
    r_type = st.selectbox("作成する地図の種類", options=[""] + list(MAP_TYPES.keys()), 
                          format_func=lambda x: "ー" if x == "" else f"{x} {MAP_TYPES[x]}")
    
    if r_type:
        p_type = st.selectbox("目印を描画しますか？", options=[""] + list(POINT_OPTIONS.keys()), 
                              format_func=lambda x: "ー" if x == "" else f"{x} {POINT_OPTIONS[x]}", help="地図上の任意の地点に×印を描画できます")
        
        lon, lat = None, None
        if p_type == "a":
            lon = st.text_input('経度を入力してください', placeholder='例：132.77 (愛媛大学 経度)', help="十進法で入力")
            lat = st.text_input('緯度を入力してください', placeholder='例：33.85 (愛媛大学 緯度)', help="十進法で入力")

        df = load_river_data(r_type)
        r_name = st.text_input('河川名を入力してください', placeholder='例：重信川', help="全角，正式名称で 川まで入力")
        
        if r_name:
            try:
                river_info = df.loc[r_name]
                st.dataframe(river_info)
                
                r_code = river_info["河川コード"]
                if isinstance(r_code, pd.Series):
                    if len(r_code.unique()) == 1:
                        r_code = r_code.iloc[0]
                        st.write(f"自動選択された河川コード: {r_code}")
                    else:
                        r_code = st.text_input('河川コードを入力してください（上記リストからコピー&ペースト）', 
                                               placeholder='例:8808010001', help="半角で入力，上記のリストからコピペ")
                elif isinstance(r_code, str):
                    st.write(f"自動選択された河川コード: {r_code}")
                
                if r_code:
                    st.write(f"選択された河川コード: {r_code}")
                    fig = create_map(r_type, r_code, p_type, lon, lat)
                    
                    with tempfile.NamedTemporaryFile(suffix=".png") as tmpfile:
                        fig.savefig(tmpfile.name)
                        tmpfile.seek(0)
                        image_buffer = io.BytesIO(tmpfile.read())
                    
                    st.image(image_buffer, caption=f"{r_name}_{r_code}_{r_type}", use_column_width=True)
                    
                    st.download_button(
                        label="ダウンロード",
                        data=image_buffer,
                        file_name=f"{r_name}_{r_code}_{r_type}.png",
                        mime="image/png"
                    )
            
            except KeyError:
                st.error(f"河川名 '{r_name}' が見つかりません。正しい名前を入力してください。")
    else:
        st.write("↑地図の種類を選択してください↑")

if __name__ == "__main__":
    main()