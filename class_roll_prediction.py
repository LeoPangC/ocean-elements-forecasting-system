import os
import copy
import warnings
import numpy as np
import matplotlib.pyplot as plt
from keras.models import load_model
from sklearn import preprocessing
from cartopy import crs as ccrs
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
from utils import create_dataset, get_asc_header


class RollPrediction(object):
    def __init__(
            self,
            var_simple='v10',
            absolute_path='',
            model='sst_r1_single_ConvLSTM_u__single_ConvLSTM_s_e100.h5',
            region='r1',
            split_num=8,
            data_max=None,
            data_min=None
    ):
        """
        构造函数
        :param var_simple: string，预测的要素类型
        :param model: string，需要读取的模型文件
        :param region: string，预测区域
        :param split_num: int，24小时分成的段数
        :param data_max: float，归一化的最大值
        :param data_min: float，归一化的最小值
        """

        self.fig = None
        warnings.filterwarnings("ignore")
        os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
        os.environ["CUDA_VISIBLE_DEVICES"] = "0"

        self.s_test_predict = None
        self.s_test_predict_copy = None
        self.split_num = split_num
        self.region = region
        self.absolute_path = absolute_path

        self.var_simple = var_simple
        npy_data = np.load(os.path.join(self.absolute_path, 'data', self.var_simple, 'npy_data_' + self.region + '.npy'))
        (c, self.dimX, self.dimY) = npy_data.shape

        if self.var_simple == 'swh':
            self.mask = copy.deepcopy(npy_data[0])
            self.mask[np.where(self.mask > 100)] = -1
            self.mask[np.where(self.mask > 0)] = 1
            npy_data[np.where(npy_data > 100)] = 0

        if data_min:
            self.__elem_data_min = data_min
        else:
            self.__elem_data_min = float(np.min(npy_data)) + 1
        if data_max:
            self.__elem_data_max = data_max
        else:
            self.__elem_data_max = float(np.max(npy_data)) + 1

        scaler_elem = np.zeros(shape=(self.dimX, self.dimY))
        scaler_elem[0][:] = self.__elem_data_min
        scaler_elem[-1][:] = self.__elem_data_max

        # 实现归一化
        self.elem_scaler = preprocessing.MinMaxScaler()
        self.elem_scaler.fit(scaler_elem)
        elem_year_scaler = np.zeros(npy_data.shape)
        for j in range(0, npy_data.shape[0]):
            elem_year_scaler[j] = self.elem_scaler.transform(npy_data[j])

        elem_year_scaler_x = create_dataset(elem_year_scaler, self.split_num)
        self.elem_testX = np.expand_dims(elem_year_scaler_x, axis=-1)

        self.s_model = load_model(os.path.join(self.absolute_path, 'models', model))

    def predict_elements(self):
        """
        进行预测操作
        """
        self.s_test_predict = self.s_model.predict(self.elem_testX)
        self.s_test_predict = self.s_test_predict[:, :, :, 0]
        self.s_test_predict_copy = copy.deepcopy(self.s_test_predict)
        for j in range(0, self.s_test_predict.shape[0]):
            self.s_test_predict_copy[j] = self.elem_scaler.inverse_transform(self.s_test_predict[j])

    def post_process(self):
        """
        后处理操作，滚动预测时需要使用，其他不需要
        """
        self.elem_testX = self.elem_testX.reshape(self.split_num, self.dimX, self.dimY)
        # for j in range(0, self.elem_testX.shape[0]):
        #     self.elem_testX[j] = self.elem_scaler.inverse_transform(self.elem_testX[j])
        self.elem_testX = np.concatenate((self.elem_testX, self.s_test_predict))
        # npy_data = self.elem_testX

        # scaler_elem = np.zeros(shape=(self.dimX, self.dimY))
        # scaler_elem[0][:] = self.__elem_data_min
        # scaler_elem[-1][:] = self.__elem_data_max
        #
        # self.elem_scaler = preprocessing.MinMaxScaler()
        # self.elem_scaler.fit(scaler_elem)

        # elem_year_scaler = np.zeros(npy_data.shape)
        # for j in range(0, npy_data.shape[0]):
        #     elem_year_scaler[j] = self.elem_scaler.transform(npy_data[j])
        # np.random.seed(0)

        self.elem_testX = create_dataset(self.elem_testX, self.split_num)
        # self.elem_testX = elem_year_scaler_x
        self.elem_testX = np.expand_dims(self.elem_testX, axis=-1)

    def get_predict_result(self):
        return np.flip(self.s_test_predict_copy, axis=1)

    def get_lon_lat(self, south=1.0, north=30.1, west=110.0, east=134.1, step=0.25):
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

    def pre_draw(self):
        self.fig, (self.ax) = plt.subplots(1, 1, figsize=(10, 10), subplot_kw={"projection": ccrs.PlateCarree()})
        gl = self.ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True, linewidth=1.5, color='k', alpha=0.5, linestyle='--')
        gl.xlabels_top = False  # 关闭顶端标签
        gl.ylabels_right = False  # 关闭右侧标签
        gl.xformatter = LONGITUDE_FORMATTER  # x轴设为经度格式
        gl.yformatter = LATITUDE_FORMATTER  # y轴设为纬度格式

    def draw_figs(self, lat, lon):
        """
        :param lat: 纬度
        :param lon: 经度
        """
        # 画图
        self.s_test_predict_copy = np.flip(self.s_test_predict_copy, axis=1)
        temp_a = self.s_test_predict_copy[0]
        if self.var_simple == 'swh':
            temp_a = self.__swh_mask__(temp_a)
        color_max = int(temp_a.max()) + 1
        color_min = int(temp_a.min()) - 1
        n_gap = (color_max - color_min) / 20
        levels = np.arange(color_min, color_max + n_gap, n_gap)
        cbar_kwargs = {'ticks': np.arange(color_min, color_max + n_gap, n_gap * 2)}

        filled_a = self.ax.contourf(lon, lat, temp_a, levels=levels, cmap="Oranges", cbar_kwargs=cbar_kwargs)
        self.fig.colorbar(filled_a, ax=self.ax, fraction=0.045)

    def save_figs(self, fig_name='predictFig'):
        """
        :param fig_name: 存储图像名
        """
        image_dir_name = os.path.join(self.absolute_path, 'images', self.var_simple)
        if not os.path.exists(image_dir_name):
            os.mkdir(image_dir_name)
        plt.savefig(os.path.join(image_dir_name, fig_name + 'h_' + self.region + '.png'), dpi=300)

    def __swh_mask__(self, swh):
        return swh * self.mask

    def save_asc(self, fig_name, lonX, latY, step):
        self.s_test_predict_copy = np.flip(self.s_test_predict_copy, axis=1)
        asc_data = self.s_test_predict_copy[0]
        if self.var_simple == 'swh':
            asc_data = self.__swh_mask__(asc_data)
        header = get_asc_header(asc_data, lonX, latY, step)
        asc_dir_name = os.path.join(self.absolute_path, 'asc', self.var_simple)
        if not os.path.exists(asc_dir_name):
            os.mkdir(asc_dir_name)
        asc_path = os.path.join(asc_dir_name, fig_name + 'h_' + self.region + '.asc')
        with open(asc_path, 'wb') as f:
            f.write(bytes(header, 'utf-8'))
            np.savetxt(f, asc_data)
