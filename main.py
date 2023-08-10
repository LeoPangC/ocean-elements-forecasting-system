import argparse
import os
import datetime
from parameters import ele_dir
from get_elements import predict_sal, predict_elements, bias_addtion, predict_3DT_test, predict_3DS_test, predict_elements_test, predict_sst_test, predict_sal_test, predict_swh_test, predict_3DS, predict_3DT

parser = argparse.ArgumentParser(description='Ocean-Elements-Forecasting-System')

# parser.add_argument('--folder', type=str,  default=os.getcwd(), help='Absolute path')
parser.add_argument('--region', type=str, default='r1', help='Forecasting region')
parser.add_argument('--element', type=str, required=True, default='sst', help='Ocean elements')
# 7.10 去掉了Uc和Grb的选项
parser.add_argument('--type', type=str, default='Uc', help='data type, options:[Uc, Grb]')
parser.add_argument('--lat', type=str, default='2,26', help='Latitude')
parser.add_argument('--lon', type=str, default='99,123', help='Longitude')
# 7.10 分辨率参数应该变为需求，因为浪的分辨率是0.1
parser.add_argument('--resolution', type=str, required=True, default='0.25', help='Resolution')

# 7.10新增参数日期
parser.add_argument('--date', type=str, required=True, default='20210619000000', help='forcasting date')
parser.add_argument('--mode', type=str, required=True, default='F', help='running mode,options:[F, C]')
parser.add_argument('--test', type=str, required=True, default=False, help='test,options:[True, False]')

args = parser.parse_args()
assert args.mode in ['F', 'C'], 'Mode Type Error'
BJS = datetime.datetime.strptime(args.date, '%Y%m%d%H%M%S')
path = os.path.dirname(__file__)    # 项目文件路径


# 7.11 除了盐的时间分辨率是1天，其他的时间分辨率都是3小时
if args.test == 'True':
    if args.mode == 'F':
        if args.element == 'sss':
            # 本身是北京时间，所以不用变
            date_time = BJS.strftime('%Y%m%d')
            # predict_sal(path, ele_dir[args.element][args.type], date_time, args.element, args)
            predict_sal_test(path, ele_dir[args.element][args.type], date_time, args.element, args)
        elif args.element == '3DS':
            date_time = BJS.strftime('%Y%m%d')
            predict_3DS_test(path, ele_dir[args.element][args.type], date_time, args)
        elif args.element == '3DT':
            date_time = BJS.strftime('%Y%m%d')
            predict_3DT_test(path, ele_dir[args.element][args.type], date_time, args)
        else:
            date_time = BJS + datetime.timedelta(hours=-12)
            date_time_1 = date_time + datetime.timedelta(days=-1)
            date_time_1 = date_time_1.strftime('%Y%m%d')
            date_time_2 = date_time + datetime.timedelta(days=-2)
            date_time_2 = date_time_2.strftime('%Y%m%d')
            date_time = date_time.strftime('%Y%m%d')
            # source = os.path.join(date_time, ele_dir[args.element][args.type])
            source_1 = os.path.join(date_time_1, ele_dir[args.element][args.type])
            source_2 = os.path.join(date_time_2, ele_dir[args.element][args.type])

            # predict_elements(path, source_1, source_2, args.element, args)
            if args.element == 'win':
                predict_elements_test(path, date_time, source_1, source_2, args.element, args)
            elif args.element == 'swh':
                predict_swh_test(path, ele_dir[args.element][args.type], date_time, args.element, args)
            else:
                predict_sst_test(path, ele_dir[args.element][args.type], date_time, args.element, args)
    elif args.mode == 'C':
        date_time = BJS + datetime.timedelta(hours=-12)
        date_time = date_time.strftime('%Y%m%d%H%M%S')
        date_folder = date_time[:8]
        hour = int(date_time[8:10])
        source = os.path.join(date_folder, ele_dir[args.element][args.type])
        bias_addtion(path, source, hour, args)
else:
    if args.mode == 'F':
        if args.element == 'sss':
            # 本身是北京时间，所以不用变
            date_time = BJS.strftime('%Y%m%d')
            predict_sal(path, ele_dir[args.element][args.type], date_time, args.element, args)
            # predict_sal_test(path, ele_dir[args.element][args.type], date_time, args.element, args)
        elif args.element == '3DS':
            date_time = BJS.strftime('%Y%m%d')
            predict_3DS(path, ele_dir[args.element][args.type], date_time, args)
        elif args.element == '3DT':
            date_time = BJS.strftime('%Y%m%d')
            predict_3DT(path, ele_dir[args.element][args.type], date_time, args)
        else:
            date_time = BJS + datetime.timedelta(hours=-12)
            date_time_1 = date_time + datetime.timedelta(days=-1)
            date_time_1 = date_time_1.strftime('%Y%m%d')
            date_time_2 = date_time + datetime.timedelta(days=-2)
            date_time_2 = date_time_2.strftime('%Y%m%d')
            # date_time = date_time.strftime('%Y%m%d')
            # source = os.path.join(date_time, ele_dir[args.element][args.type])
            source_1 = os.path.join(date_time_1, ele_dir[args.element][args.type])
            source_2 = os.path.join(date_time_2, ele_dir[args.element][args.type])

            predict_elements(path, source_1, source_2, args.element, args)
    elif args.mode == 'C':
        date_time = BJS + datetime.timedelta(hours=-12)
        date_time = date_time.strftime('%Y%m%d%H%M%S')
        date_folder = date_time[:8]
        hour = int(date_time[8:10])
        source = os.path.join(date_folder, ele_dir[args.element][args.type])
        bias_addtion(path, source, hour, args)