import pygmt

fig = pygmt.Figure()

def plot_x(lon,lat):
    fig.plot(x=lon, y=lat, style="x0.8c", pen="1.5p,red")
