import os
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cf
import matplotlib.ticker as mticker
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER


# 画contourf
def cf_plot(ax, lon, lat, data, fig):
    color_min = int(data.min()) - 1
    color_max = int(data.max()) + 1
    n_gap = (color_max - color_min) / 20
    levels = np.arange(color_min, color_max + n_gap, n_gap)

    ax.spines['geo'].set_linewidth(0.1)
    ax.add_feature(cf.COASTLINE.with_scale('50m'), lw=0.5, alpha=0.3)
    ax.add_feature(cf.LAND.with_scale('50m'), lw=0.5, alpha=0.3, color='#E8E6E7')
    # colorbar设置
    cbar_kwargs = {'ticks': np.arange(color_min, color_max + n_gap, n_gap)}

    cx = ax.contourf(lon, lat, data, levels=levels, cmap="Blues", cbar_kwargs=cbar_kwargs)
    # cx = ax.contourf(lon, lat, data, cmap='RdBu_r', levels=levels, transform=ccrs.PlateCarree())
    gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True, linewidth=0, alpha=0.5, linestyle='--')
    # gl = ax.gridlines(draw_labels=True, crs=ccrs.PlateCarree(), linewidth=1.5, alpha=0.5)
    gl.top_labels = False
    gl.right_labels = False
    gl.xformatter = LONGITUDE_FORMATTER
    gl.yformatter = LATITUDE_FORMATTER
    gl.xlabel_style = {'size': 10}
    gl.ylabel_style = {'size': 10}
    cb = fig.colorbar(cx, shrink=0.7, ax=ax, orientation='horizontal', pad=0.1,
                      format=mticker.FormatStrFormatter('%.0f'))
    cb.ax.tick_params(labelsize=10, length=0.5, width=0.5)
    cb.ax.spines['bottom'].set_visible(False)
    cb.outline.set_linewidth(0.3)
    c_gaps = (color_max - color_min) / 4
    cb.ax.locator_params(nbins=5)
    cb.set_ticks(np.arange(color_min, color_max + c_gaps, c_gaps))
    cb.get_ticks()


# 画流场图quiver
def plotuv(ax, lon, lat, u, v):
    q = ax.quiver(lon, lat, u, v, alpha=0.75, transform=ccrs.PlateCarree())


# 查找最近的值的索引，用于匹配数值
def getnearpos(array, value):
    idx = (np.abs(array - value)).argmin()
    return idx


def create_dataset(data, time_step):
    data_set = []
    data_set.append(data[data.shape[0] - time_step:])
    return np.array(data_set)


def get_lat_lon(south=1.0, north=30.1, west=110.0, east=134.1, step=0.25):
    """
    计算经纬度幅度
    :param south:float，南纬边界
    :param north:float，北纬边界
    :param west:float，西经边界
    :param east:float，东经边界
    :param step:float，步幅
    :return: lon，lat
    """
    lat = np.arange(south, north + 0.001, step)
    lon = np.arange(west, east + 0.001, step)
    return lat, lon


def draw_current_figs(lat, lon, cur_sped, cur_dir, u_sped, v_sped):
    fig, (ax) = plt.subplots(1, 1, figsize=(10, 10), subplot_kw={"projection": ccrs.PlateCarree()})
    cf_plot(ax, lon, lat, cur_sped, fig)
    plotuv(ax, lon, lat, u_sped, v_sped)


def save_figs(fig_name='predictFig', absolute_path='', var_simple='cur', region='r1'):
    """
    :param region:
    :param absolute_path:
    :param var_simple:
    :param fig_name: 存储图像名
    """
    image_dir_name = os.path.join(absolute_path, 'images', var_simple)
    if not os.path.exists(image_dir_name):
        os.mkdir(image_dir_name)
    plt.savefig(os.path.join(image_dir_name, fig_name + 'h_' + region + '.png'), dpi=300)
