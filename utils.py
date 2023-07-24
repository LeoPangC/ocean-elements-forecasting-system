import os
import numpy as np
import json
import matplotlib.pyplot as plt


# 画contourf
# def cf_plot(ax, lon, lat, data, fig):
#     color_min = int(data.min()) - 1
#     color_max = int(data.max()) + 1
#     n_gap = (color_max - color_min) / 20
#     levels = np.arange(color_min, color_max + n_gap, n_gap)
#
#     ax.spines['geo'].set_linewidth(0.1)
#     ax.add_feature(cf.COASTLINE.with_scale('50m'), lw=0.5, alpha=0.3)
#     ax.add_feature(cf.LAND.with_scale('50m'), lw=0.5, alpha=0.3, color='#E8E6E7')
#     # colorbar设置
#     cbar_kwargs = {'ticks': np.arange(color_min, color_max + n_gap, n_gap)}
#
#     cx = ax.contourf(lon, lat, data, levels=levels, cmap="Blues", cbar_kwargs=cbar_kwargs)
#     # cx = ax.contourf(lon, lat, data, cmap='RdBu_r', levels=levels, transform=ccrs.PlateCarree())
#     gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True, linewidth=0, alpha=0.5, linestyle='--')
#     # gl = ax.gridlines(draw_labels=True, crs=ccrs.PlateCarree(), linewidth=1.5, alpha=0.5)
#     gl.top_labels = False
#     gl.right_labels = False
#     gl.xformatter = LONGITUDE_FORMATTER
#     gl.yformatter = LATITUDE_FORMATTER
#     gl.xlabel_style = {'size': 10}
#     gl.ylabel_style = {'size': 10}
#     cb = fig.colorbar(cx, shrink=0.7, ax=ax, orientation='horizontal', pad=0.1,
#                       format=mticker.FormatStrFormatter('%.0f'))
#     cb.ax.tick_params(labelsize=10, length=0.5, width=0.5)
#     cb.ax.spines['bottom'].set_visible(False)
#     cb.outline.set_linewidth(0.3)
#     c_gaps = (color_max - color_min) / 4
#     cb.ax.locator_params(nbins=5)
#     cb.set_ticks(np.arange(color_min, color_max + c_gaps, c_gaps))
#     cb.get_ticks()


# 画流场图quiver
# def plotuv(ax, lon, lat, u, v):
#     q = ax.quiver(lon, lat, u, v, alpha=0.75, transform=ccrs.PlateCarree())


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


# def draw_current_figs(lat, lon, cur_sped, cur_dir, u_sped, v_sped):
#     fig, (ax) = plt.subplots(1, 1, figsize=(10, 10), subplot_kw={"projection": ccrs.PlateCarree()})
#     cf_plot(ax, lon, lat, cur_sped, fig)
#     plotuv(ax, lon, lat, u_sped, v_sped)


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


# 2023.5.15 增加需求：存储为asc文件
# 2023.6.7 增加四个边框
def get_asc_header_archor(tar_data, lon, lat, step, nodata=-32767, gap=0):
    (dimX, dimY) = tar_data.shape
    archor = np.zeros([dimX + 2 * gap, dimY + 2 * gap])
    if gap != 0:
        archor[gap:-gap, gap:-gap] = tar_data
    else:
        archor = tar_data
    (dimX, dimY) = archor.shape
    lon = lon - step * gap
    lat = lat - step * gap
    header = 'ncols        {}\n'.format(dimY)
    header += 'nrows        {}\n'.format(dimX)
    header += 'xllcorner    {}\n'.format(lon)
    header += 'yllcorner    {}\n'.format(lat)
    header += 'cellsize    {}\n'.format(step)
    header += 'NODATA_value {}\n'.format(nodata)
    return header, archor


def get_asc_header(tar_data, lon, lat, step):
    (dimX, dimY) = tar_data.shape
    header = 'ncols        {}\n'.format(dimY)
    header += 'nrows        {}\n'.format(dimX)
    header += 'xllcorner    {}\n'.format(lon)
    header += 'yllcorner    {}\n'.format(lat)
    header += 'cellsize    {}\n'.format(step)
    header += 'NODATA_value -32767\n'
    return header


def save_asc(absolute_path, asc_data, fig_name, lonX, latY, step, var_simple):
    # self.s_test_predict_copy = np.flip(self.s_test_predict_copy, axis=1)
    # asc_data = self.s_test_predict_copy[0]
    # asc_data = self.get_predict_result()[0]
    (header, asc_data) = get_asc_header_archor(asc_data, lonX, latY, step)
    # header = get_asc_header(asc_data, lonX, latY, step)
    asc_dir_name = os.path.join(absolute_path, 'asc', var_simple)
    if not os.path.exists(asc_dir_name):
        os.mkdir(asc_dir_name)
    asc_path = os.path.join(asc_dir_name, fig_name + 'h_r1.asc')
    # asc_data类型是ndarray
    with open(asc_path, 'wb') as f:
        f.write(bytes(header, 'utf-8'))
        np.savetxt(f, asc_data)


def save_json(absolute_path, data, fig_name, date, var_simple):
    if var_simple == '3DT':
        data = data - 273.15
    data = np.flip(data, axis=0)
    data = np.reshape(data, (1, -1))
    data = np.squeeze(data)
    date_dir_name = os.path.join(absolute_path, 'data/forcast', date)
    if not os.path.exists(date_dir_name):
        os.mkdir(date_dir_name)
    asc_folder = os.path.join(date_dir_name, var_simple)
    if not os.path.exists(asc_folder):
        os.mkdir(asc_folder)
    json_path = os.path.join(asc_folder, 'Forcast' + var_simple + '_' + fig_name + '.json')
    with open(json_path, 'w') as f:
        json.dump(data.tolist(), f)


def save_npy(absolute_path, data, fig_name, date, var_simple):
    if var_simple == '3DT':
        data = data - 273.15
    # data = np.flip(data, axis=0)
    # data = np.reshape(data, (1, -1))
    # data = np.squeeze(data)
    date_dir_name = os.path.join(absolute_path, 'data/forcast', date)
    if not os.path.exists(date_dir_name):
        os.mkdir(date_dir_name)
    npy_folder = os.path.join(date_dir_name, var_simple)
    if not os.path.exists(npy_folder):
        os.mkdir(npy_folder)
    npy_path = os.path.join(npy_folder, 'Forcast' + var_simple + '_' + fig_name + '.npy')
    np.save(npy_path, data)
