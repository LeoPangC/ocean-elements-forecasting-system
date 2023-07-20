from netCDF4 import Dataset
import pygrib as pg
import numpy as np
import os


class CombatData(object):
    def __init__(self, sub_folder=None, var_simple='u10', region='r1', absolute_path=''):
        """
        构造函数
        :param sub_folder: string，data文件夹中存储nc数据文件的文件路径
        :param var_simple: string，npy数据存储文件，用于创建文件
        :param region: string，预测区域
        :param absolute_path: string，项目绝对路径
        """
        self.root_dir = os.path.join(absolute_path, 'data')
        raw_folder = 'raw_data'
        self.npy_data = np.array([])
        if sub_folder:
            self.data_dir = os.path.join(self.root_dir, raw_folder, sub_folder)
        else:
            self.data_dir = os.path.join(self.root_dir, raw_folder)
        # self.var = var
        self.region = region
        self.npy_folder_name = var_simple
        self.data_files = []
        self.data_files = [file for file in os.listdir(self.data_dir) if '.nc' in file or '.grb' in file]
        self.data_files.sort()

    def trans_nc_to_npy(self, lat_lon, depth=0):
        """
        提取nc数据，将nc转为array数据类型
        :param depth: int
        :param lat_lon: list
        """
        # 7.10 更新,只取当天数据，即前8个数据
        for nc in self.data_files[:8]:
            # if 'order' in nc:
            self.nc_to_npy(lat=(lat_lon['south'], lat_lon['north']),
                           lon=(lat_lon['west'], lat_lon['east']),
                           depth=depth,
                           nc_name=nc)
            # else:
            #     self.nc_to_npy(lat=lat_lon[1]['lat'], lon=lat_lon[1]['lon'], step=lat_lon[1]['step'], nc_name=nc)

    def trans_nc_to_npy_one(self, lat_lon, hour=0):
        index = hour // 3
        nc = self.data_files[index]
        self.nc_to_npy(lat=(lat_lon['south'], lat_lon['north']),
                       lon=(lat_lon['west'], lat_lon['east']),
                       nc_name=nc)

    def nc_to_npy(self, lat=(124.0, 241.0), lon=(320.0, 417.0), depth=0, nc_name=''):
        """
        将nc转为array数据类型
        lat=(124.0, 241.0), lon=(320.0, 417.0), step=1
        :param lon: tuple，经度范围
        :param lat: tuple，纬度范围
        :param depth: int，深度
        :param nc_name: string，文件名
        """
        nc_data = os.path.join(self.data_dir, nc_name)
        dataloader = DataLoader(nc_data, lat, lon, self.npy_folder_name, depth)
        tmp_np = dataloader.get_data()
        try:
            self.npy_data = np.concatenate((self.npy_data, tmp_np))
        except (UnboundLocalError, ValueError):
            self.npy_data = tmp_np

    def trans_grb_to_npy(self, lat=(18.5, 22.0), lon=(116.5, 120.0)):
        """
        提取grb数据，将grb转为array数据类型
        :param lon: tuple，经度范围
        :param lat: tuple，纬度范围
        """
        for grb in self.data_files:
            grb_data = os.path.join(self.data_dir, grb)
            gf = pg.open(grb_data)
            try:
                var_data = gf.select(name=self.var)[0]
            except ValueError:
                pass
            var_data, lats, lons = var_data.data(lat1=lat[0], lat2=lat[1], lon1=lon[0], lon2=lon[1])
            # var_data = np.flip(var_data, axis=1)
            tmp_np = np.array(var_data)
            (self.dimX, self.dimY) = tmp_np.shape
            try:
                self.npy_data = np.concatenate((self.npy_data, tmp_np))
            except (UnboundLocalError, ValueError):
                self.npy_data = tmp_np

    def gen_npy(self, index=''):
        """
        将数据保存在npy文件里
        """
        npy_dir_name = os.path.join(self.root_dir, self.npy_folder_name)
        if not os.path.exists(npy_dir_name):
            os.mkdir(npy_dir_name)
        # self.npy_data = self.npy_data.reshape(-1, self.dimX, self.dimY)
        # np.savetxt(os.path.join(npy_dir_name, 'asc_data_' + self.region + '.asc'), self.npy_data[-1])
        np.save(os.path.join(npy_dir_name, 'npy_data_' + self.region + '_' + str(index) + '.npy'), self.npy_data)

    def get_npy(self):
        """
        获取array数据
        :return: np.array，npy数据
        """
        return self.npy_data


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
        if element == 'sss' or element == '3DS':
            # lat_s = list(ds.variables[lat_lon[2]][:, 0].data)
            # lon_s = list(ds.variables[lat_lon[3]][0, :].data)
            var_data = ds.variables[lat_lon[6]][:, depth, 919:1160, 2789:3030].data
        elif element == 'sst':
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

# r1_lat = (194, 209)
# r1_lon = (346, 361)
# combatData = CombatData('2021010112/UT')
# combatData.trans_nc_to_npy(r1_lat, r1_lon)
# # combatData.trans_nc_to_npy('10 metre U windU component')
# combatData.gen_npy()