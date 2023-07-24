import os
import copy
import warnings
import numpy as np
import matplotlib.pyplot as plt
from keras.models import load_model
from sklearn import preprocessing
# from cartopy import crs as ccrs
# from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
from utils import create_dataset, get_asc_header_archor, get_asc_header


class RollPrediction(object):
    def __init__(
            self,
            var_simple='v10',
            absolute_path='',
            model='sst_r1_single_ConvLSTM_u__single_ConvLSTM_s_e100.h5',
            region='r1',
            split_num=8,
            data_max=None,
            data_min=None,
            index=''
    ):
        """
        构造函数
        :param var_simple: string，预测的要素类型
        :param model: string，需要读取的模型文件
        :param region: string，预测区域
        :param split_num: int，24小时分成的段数
        :param data_max: float，归一化的最大值
        :param data_min: float，归一化的最小值
        :param index: string，主要用来区分风浪的切片，其他要素默认为空
        """

        # self.fig = None
        # warnings.filterwarnings("ignore")
        os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
        os.environ["CUDA_VISIBLE_DEVICES"] = "0"

        self.s_test_predict = None
        self.s_test_predict_copy = None
        self.split_num = split_num
        self.region = region
        self.absolute_path = absolute_path

        self.var_simple = var_simple

        self.data_min = data_min
        self.data_max = data_max
        self.model = model

        self.s_model = load_model(os.path.join(self.absolute_path, 'models', self.model))

    def data_pre_process(self, npy_data, mode='F', bc_max=None, bc_min=None):
        (c, self.dimX, self.dimY) = npy_data.shape

        if self.var_simple == 'swh':
            self.mask = copy.deepcopy(npy_data[0])
            self.mask[np.where(self.mask > 100)] = -1
            self.mask[np.where(self.mask > 0)] = 1
            npy_data[np.where(npy_data > 100)] = 0

        if self.data_min:
            self.__elem_data_min = self.data_min
        else:
            self.__elem_data_min = np.min(npy_data)
        if self.data_max:
            self.__elem_data_max = self.data_max
        else:
            self.__elem_data_max = np.max(npy_data)

        # scaler_elem = np.zeros(shape=(self.dimX, self.dimY))
        # scaler_elem[0][:] = self.__elem_data_min
        # scaler_elem[-1][:] = self.__elem_data_max

        # 实现归一化
        # self.elem_scaler = preprocessing.MinMaxScaler()
        # self.elem_scaler.fit(scaler_elem)
        # elem_year_scaler = np.zeros(npy_data.shape)
        # for j in range(0, npy_data.shape[0]):
        #     elem_year_scaler[j] = self.elem_scaler.transform(npy_data[j])
        elem_year_scaler = (npy_data - self.__elem_data_min) / (self.__elem_data_max - self.__elem_data_min)

        if mode == 'C':
            self.__elem_data_max = bc_max
            self.__elem_data_min = bc_min
            # scaler_elem[0][:] = bc_min
            # scaler_elem[-1][:] = bc_max
            # self.elem_scaler.fit(scaler_elem)
            self.elem_testX = elem_year_scaler.reshape((1, self.dimX, self.dimY, c))
        else:
            elem_year_scaler_x = create_dataset(elem_year_scaler, self.split_num)
            self.elem_testX = np.expand_dims(elem_year_scaler_x, axis=-1)

    def predict_elements(self):
        """
        进行预测操作
        """

        self.s_test_predict = self.s_model.predict(self.elem_testX)
        self.s_test_predict = self.s_test_predict[:, :, :, 0]
        self.s_test_predict_copy = copy.deepcopy(self.s_test_predict)
        self.s_test_predict_copy = self.__elem_data_min + self.s_test_predict_copy * (self.__elem_data_max - self.__elem_data_min)
        # for j in range(0, self.s_test_predict.shape[0]):
        #     self.s_test_predict_copy[j] = self.elem_scaler.inverse_transform(self.s_test_predict[j])

    def post_process(self):
        """
        后处理操作，滚动预测时需要使用，其他不需要
        """
        self.elem_testX = self.elem_testX.reshape(self.split_num, self.dimX, self.dimY)
        # for j in range(0, self.elem_testX.shape[0]):
        #     self.elem_testX[j] = self.elem_scaler.inverse_transform(self.elem_testX[j])
        self.elem_testX = np.concatenate((self.elem_testX, self.s_test_predict))

        self.elem_testX = create_dataset(self.elem_testX, self.split_num)
        # self.elem_testX = elem_year_scaler_x
        self.elem_testX = np.expand_dims(self.elem_testX, axis=-1)
        return self.elem_testX[0, :, :, :, 0]

    def get_predict_result(self):
        # return np.flip(self.s_test_predict_copy, axis=1)
        return self.s_test_predict_copy

    def get_lon_lat(self, south=1.0, north=30.1, west=110.0, east=134.1, step=0.25):
        """
        计算经纬度列表
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

    # def pre_draw(self):
    #     self.fig, (self.ax) = plt.subplots(1, 1, figsize=(10, 10), subplot_kw={"projection": ccrs.PlateCarree()})
    #     gl = self.ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True, linewidth=1.5, color='k', alpha=0.5, linestyle='--')
    #     gl.xlabels_top = False  # 关闭顶端标签
    #     gl.ylabels_right = False  # 关闭右侧标签
    #     gl.xformatter = LONGITUDE_FORMATTER  # x轴设为经度格式
    #     gl.yformatter = LATITUDE_FORMATTER  # y轴设为纬度格式

    def draw_figs(self, lat, lon):
        """
        :param lat: 纬度
        :param lon: 经度
        """
        # 画图
        # self.s_test_predict_copy = np.flip(self.s_test_predict_copy, axis=1)
        # temp_a = self.s_test_predict_copy[0]
        temp_a = self.get_predict_result()[0]
        temp_a = self.__swh_mask__(temp_a)
        temp_a = self.__k2c__(temp_a)
        color_max = int(temp_a.max()) + 1
        color_min = int(temp_a.min()) - 1
        n_gap = (color_max - color_min) / 20
        levels = np.arange(color_min, color_max + n_gap, n_gap)
        cbar_kwargs = {'ticks': np.arange(color_min, color_max + n_gap, n_gap * 2)}

        filled_a = self.ax.contourf(lon, lat, temp_a, levels=levels, cmap="Blues", cbar_kwargs=cbar_kwargs)
        self.fig.colorbar(filled_a, ax=self.ax, fraction=0.045)

    def save_figs(self, fig_name='predictFig'):
        """
        :param fig_name: 存储图像名
        """
        image_dir_name = os.path.join(self.absolute_path, 'images', self.var_simple)
        if not os.path.exists(image_dir_name):
            os.mkdir(image_dir_name)
        plt.savefig(os.path.join(image_dir_name, fig_name + 'h_' + self.region + '.png'), dpi=300)

    def __swh_mask__(self, data):
        if self.var_simple == 'swh':
            return data * self.mask
        return data

    def __k2c__(self, data):
        if self.var_simple == '3DT':
            return data - 273.15
        return data

    def save_asc(self, fig_name, lonX, latY, step, date, hour=None, nodata=-32767, mode='F'):
        asc_data = self.get_predict_result()[0]
        asc_data = np.flip(asc_data, axis=0)
        # asc_data = self.__swh_mask__(asc_data)
        asc_data = self.__k2c__(asc_data)
        (header, asc_data) = get_asc_header_archor(asc_data, lonX, latY, step, nodata)
        date_dir_name = os.path.join(self.absolute_path, 'data/forcast', date)
        if not os.path.exists(date_dir_name):
            os.mkdir(date_dir_name)
        if mode == 'F':
            asc_folder = os.path.join(date_dir_name, self.var_simple)
            if not os.path.exists(asc_folder):
                os.mkdir(asc_folder)
            asc_path = os.path.join(asc_folder, 'Forcast' + self.var_simple + '_' + fig_name + '.asc')
        elif mode == 'C':
            asc_folder = os.path.join(date_dir_name, 'bc_' + self.var_simple)
            if not os.path.exists(asc_folder):
                os.mkdir(asc_folder)
            asc_path = os.path.join(asc_folder, fig_name + '_' + str(hour) + 'h.asc')
        # asc_data类型是ndarray
        with open(asc_path, 'wb') as f:
            f.write(bytes(header, 'utf-8'))
            np.savetxt(f, asc_data)

    def save_npy(self, fig_name, date, hour=None, mode='F'):
        npy_data = self.get_predict_result()[0]
        npy_data = np.flip(npy_data, axis=0)
        npy_data = self.__k2c__(npy_data)
        date_dir_name = os.path.join(self.absolute_path, 'data/forcast', date)
        if not os.path.exists(date_dir_name):
            os.mkdir(date_dir_name)
        if mode == 'F':
            npy_folder = os.path.join(date_dir_name, self.var_simple)
            if not os.path.exists(npy_folder):
                os.mkdir(npy_folder)
            npy_path = os.path.join(npy_folder, 'Forcast' + self.var_simple + '_' + fig_name + '.npy')
        elif mode == 'C':
            npy_folder = os.path.join(date_dir_name, 'bc_' + self.var_simple)
            if not os.path.exists(npy_folder):
                os.mkdir(npy_folder)
            npy_path = os.path.join(npy_folder, fig_name + '_' + str(hour) + 'h.npy')

        np.save(npy_path, npy_data)

