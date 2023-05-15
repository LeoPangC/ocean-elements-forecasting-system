from netCDF4 import Dataset
import pygrib as pg
import numpy as np
import os


class CombatData(object):
    def __init__(self, sub_folder=None, var='10 metre U wind component', var_simple='u10', region='r1', absolute_path=''):
        """
        构造函数
        :param sub_folder: string，data文件夹中存储nc数据文件的文件路径，如：'2021010112/TEM'
        :param var: string，提取要素名
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
        self.var = var
        self.region = region
        self.npy_folder_name = var_simple
        self.data_files = [file for file in os.listdir(self.data_dir) if '.nc' or '.grb' in file]
        self.data_files.sort()

    def trans_nc_to_npy(self, lat_lon=[]):
        """
        提取nc数据，将nc转为array数据类型
        :param lat_lon: list
        """
        for nc in self.data_files:
            if 'order' in nc:
                self.nc_to_npy(lat=lat_lon[0]['lat'], lon=lat_lon[0]['lon'], step=lat_lon[0]['step'], nc_name=nc)
            else:
                self.nc_to_npy(lat=lat_lon[1]['lat'], lon=lat_lon[1]['lon'], step=lat_lon[1]['step'], nc_name=nc)

    def nc_to_npy(self, lat=(124.0, 241.0), lon=(320.0, 417.0), step=1, nc_name=''):
        """
        将nc转为array数据类型
        lat=(124.0, 241.0), lon=(320.0, 417.0), step=1
        :param lon: tuple，经度范围
        :param lat: tuple，纬度范围
        :param step: int，确定要素数据分辨率
        :param nc_name: string，文件名
        """
        nc_data = os.path.join(self.data_dir, nc_name)
        nf = Dataset(nc_data)
        var_data = nf.variables[self.var][:].data
        if self.var == 'CUR' or self.var == 'CVR' or self.var == 'TEM' or self.var == 'SAL':
            var_data = var_data[0, 0, lat[0]: lat[1]: step, lon[0]: lon[1]: step]
        else:
            var_data = var_data[0, lat[0]: lat[1]: step, lon[0]: lon[1]: step]
            var_data = np.flip(var_data, axis=1)
        tmp_np = np.array(var_data)
        (self.dimX, self.dimY) = tmp_np.shape
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

    def gen_npy(self):
        """
        将数据保存在npy文件里
        """
        npy_dir_name = os.path.join(self.root_dir, self.npy_folder_name)
        if not os.path.exists(npy_dir_name):
            os.mkdir(npy_dir_name)
        self.npy_data = self.npy_data.reshape(-1, self.dimX, self.dimY)
        # np.savetxt(os.path.join(npy_dir_name, 'asc_data_' + self.region + '.asc'), self.npy_data[-1])
        np.save(os.path.join(npy_dir_name, 'npy_data_' + self.region + '.npy'), self.npy_data)

    def get_npy(self):
        """
        获取array数据
        :return: np.array，npy数据
        """
        return self.npy_data


# r1_lat = (194, 209)
# r1_lon = (346, 361)
# combatData = CombatData('2021010112/UT')
# combatData.trans_nc_to_npy(r1_lat, r1_lon)
# # combatData.trans_nc_to_npy('10 metre U windU component')
# combatData.gen_npy()
