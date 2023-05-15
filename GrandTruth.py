from netCDF4 import Dataset
import numpy as np
import matplotlib.pyplot as plt
from utils import get_lat_lon
from cartopy import crs as ccrs
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER

for i in range(4):
    nf = Dataset('./data/raw_data/new/TEM/orderTEM_0{0:d}.nc'.format(24 + i * 3))
    var_data = nf.variables['TEM'][:].data
    var_data = var_data[0, 0, 0: 36: 1, 55: 91: 1]
    # var_data = np.array(var_data)

    #画图
    fig, (ax) = plt.subplots(1, 1, figsize=(10, 10), subplot_kw={"projection": ccrs.PlateCarree()})
    gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True, linewidth=1.5, color='k', alpha=0.5,
                           linestyle='--')
    gl.xlabels_top = False  # 关闭顶端标签
    gl.ylabels_right = False  # 关闭右侧标签
    gl.xformatter = LONGITUDE_FORMATTER  # x轴设为经度格式
    gl.yformatter = LATITUDE_FORMATTER  # y轴设为纬度格式

    color_max = 31.0
    color_min = 28.0
    n_gap = (color_max - color_min) / 20
    levels = np.arange(color_min, color_max + n_gap, n_gap)
    cbar_kwargs = {'ticks': np.arange(color_min, color_max + n_gap, n_gap * 2)}

    lat, lon = get_lat_lon(south=15,
                           north=18.5,
                           west=110.5,
                           east=114,
                           step=0.1)
    filled_b = ax.contourf(lon, lat, var_data, levels=levels, cmap="Oranges", cbar_kwargs=cbar_kwargs)
    fig.colorbar(filled_b, ax=ax, fraction=0.045)
    plt.savefig('./images/sst_GT/{}h_r1.png'.format((i+1)*3), dpi=300)