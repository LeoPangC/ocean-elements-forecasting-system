import os
import argparse
import datetime
import numpy as np
from netCDF4 import Dataset
from utils import save_asc


class DataLoader(object):

    def __init__(self, data_path, lat, lon, depth=0):
        """
        切割指定区域的nc文件数据
        :param data_path: string, nc文件路径
        :param lat: list, 纬度范围
        :param lon: list, 经度区域
        """
        self.data_path = data_path
        var_data = self.__read_data__()
        self.data = self.__cut_lat_lon__(var_data, lat, lon, depth)

    def __read_data__(self):
        ds = Dataset(self.data_path)
        return ds

    def __cut_lat_lon__(self, ds, lat, lon, depth=0):
        lat_lon = []
        for ll in ds.variables.keys():
            lat_lon.append(ll)
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


parser = argparse.ArgumentParser(description='Ocean-Elements-Forecasting-System')

parser.add_argument('--date', type=str, required=True, help='forcasting date')

args = parser.parse_args()

BJS = datetime.datetime.strptime(args.date, '%Y%m%d%H%M%S')
path = os.path.dirname(__file__)    # 项目文件路径

date_time = BJS + datetime.timedelta(hours=-8)
date_time = date_time.strftime('%Y%m%d%H')
date_time = date_time[:8]

raw_date_path = os.path.join(path, 'data', 'raw_data')
display_path = os.path.join(path, 'data', 'display')
date_folder = os.path.join(raw_date_path, date_time)
display_date_path = os.path.join(display_path, date_time)
if not os.path.exists(display_date_path):
    os.mkdir(display_date_path)
dir_list = os.listdir(date_folder)
for ele_folder in dir_list:
    if ele_folder == 'H03':
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
        dl = DataLoader(nc_path, [1, 27], [92, 130])
        nc_data = dl.get_data()
        npy_data = np.flip(nc_data, axis=1)
        save_asc(display_ele_path, npy_data[0], nc[:-3], 92, 1, resolution, ele_folder)