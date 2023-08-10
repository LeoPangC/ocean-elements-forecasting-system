import os
import argparse
import numpy as np
from netCDF4 import Dataset
from parameters import NODATA
from utils import fill_missing_values


var = {
    'H03': 'order',
    'TT': 'order',
    'UT': 'order',
    'VT': 'order',
    'SST': 'ERA5',
    'ERA5U': 'ERA5',
    'ERA5V': 'ERA5',
    'OCRA': 'CORA'
}


class DataLoader(object):

    def __init__(self, data_path, lat, lon, element, depth=0):
        """
        切割指定区域的nc文件数据
        :param data_path: string, nc文件路径
        :param lat: list, 纬度范围
        :param lon: list, 经度区域
        """
        self.data_path = data_path
        var_data = self.__read_data__()
        self.data = self.__cut_lat_lon__(var_data, lat, lon, element, depth)

    def __read_data__(self):
        ds = Dataset(self.data_path)
        return ds

    def __cut_lat_lon__(self, ds, lat, lon, element, depth=0):
        lat_lon = []
        for ll in ds.variables.keys():
            lat_lon.append(ll)
        if element == 'CORA':
            # lat_s = list(ds.variables[lat_lon[2]][:, 0].data)
            # lon_s = list(ds.variables[lat_lon[3]][0, :].data)
            var_data = ds.variables[lat_lon[6]][:, depth, 919:1160, 2789:3030].data
        elif element == 'ERA5':
            lat_s = list(ds.variables[lat_lon[1]][:].data)
            lon_s = list(ds.variables[lat_lon[0]][:].data)
            var_data = ds.variables[lat_lon[-1]][:].data
            var_data = var_data[:, lat_s.index(lat[1]):lat_s.index(lat[0])+1, lon_s.index(lon[0]):lon_s.index(lon[1])+1]
            var_data = np.flip(var_data, axis=1)
        else:
            # 取得数据纬度范围
            lat_s = list(ds.variables[lat_lon[0]][:].data)
            # 取得数据经度范围
            lon_s = list(ds.variables[lat_lon[1]][:].data)
            # 判断数据中是否包含指定经纬度，如包含对数据进行切割
            var_data = ds.variables[lat_lon[-1]][:].data
            if var_data.ndim == 3:
                var_data = var_data[:, lat_s.index(lat[0]):lat_s.index(lat[1])+1, lon_s.index(lon[0]):lon_s.index(lon[1])+1]
            else:
                var_data = var_data[:, depth, lat_s.index(lat[0]):lat_s.index(lat[1])+1, lon_s.index(lon[0]):lon_s.index(lon[1])+1]
        return var_data

    def get_data(self):
        return self.data


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


def save_asc(absolute_path, asc_data, fig_name, lonX, latY, step, var_simple):
    if var_simple == 'CORA':
        (header, asc_data) = get_asc_header_archor(asc_data, lonX, latY, step)
        asc_path = os.path.join(absolute_path, 'daily.asc')
    elif var_simple == 'SST':
        (header, asc_data) = get_asc_header_archor(asc_data, lonX, latY, step, nodata=NODATA['sst'])
        asc_data -= 273.15
        asc_path = os.path.join(absolute_path, fig_name + 'h.asc')
    elif var_simple == 'H03':
        (header, asc_data) = get_asc_header_archor(asc_data, lonX, latY, step, nodata=NODATA['swh'])
        asc_path = os.path.join(absolute_path, fig_name + '.asc')
    else:
        (header, asc_data) = get_asc_header_archor(asc_data, lonX, latY, step)
        asc_path = os.path.join(absolute_path, fig_name + '.asc')
    # asc_data类型是ndarray
    with open(asc_path, 'wb') as f:
        f.write(bytes(header, 'utf-8'))
        np.savetxt(f, asc_data)


parser = argparse.ArgumentParser(description='Ocean-Elements-Forecasting-System')

parser.add_argument('--date', type=str, required=True, help='forcasting date')

args = parser.parse_args()

path = os.path.dirname(__file__)    # 项目文件路径

date_time = args.date[:10]

raw_date_path = os.path.join(path, 'data', 'raw_data')
display_path = os.path.join(path, 'data', 'display')
try:
    date_folder = os.path.join(raw_date_path, date_time)
    dir_list = os.listdir(date_folder)
except:
    date_time = date_time[:-2]
    date_folder = os.path.join(raw_date_path, date_time)
    dir_list = os.listdir(date_folder)
dir_list.sort()
display_date_path = os.path.join(display_path, date_time)
if not os.path.exists(display_date_path):
    os.mkdir(display_date_path)
for ele_folder in dir_list:
    if ele_folder == 'H03' or ele_folder == 'CORA':
        resolution = 0.1
    else:
        resolution = 0.25
    ele_path = os.path.join(date_folder, ele_folder)
    display_ele_path = os.path.join(display_date_path, ele_folder)
    if not os.path.exists(display_ele_path):
        os.mkdir(display_ele_path)
    nc_list = os.listdir(ele_path)
    nc_list.sort()
    for nc in nc_list[:8]:
        nc_path = os.path.join(ele_path, nc)
        display_nc_path = os.path.join(display_ele_path, nc)
        dl = DataLoader(nc_path, [1, 27], [92, 130], var[ele_folder])
        nc_data = dl.get_data()
        npy_data = np.flip(nc_data, axis=1)
        npy_data = fill_missing_values(npy_data[0])
        save_asc(display_ele_path, npy_data, nc[:-3], 92, 1, resolution, ele_folder)