import argparse
import os
import datetime
from parameters import ele_dir
from get_elements import predict_sal, predict_elements, bias_correction, predict_3DT, predict_3DS

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

args = parser.parse_args()
assert args.mode in ['F', 'C'], 'Mode Type Error'
BJS = datetime.datetime.strptime(args.date, '%Y%m%d%H%M%S')
path = os.path.dirname(__file__)    # 项目文件路径


# 7.10 时间转换还存在问题，前端给的是北京时间，应当转换为格林尼治时间，并且文件里的0代表格林尼治时间的12点，所以应当再减去12小时
# 7.11 除了盐的时间分辨率是1天，其他的时间分辨率都是3小时
if args.mode == 'F':
    if args.element == 'sss':
        # 本身是北京时间，所以不用变
        date_time = BJS.strftime('%Y%m%d')
        predict_sal(path, ele_dir[args.element][args.type], date_time, args.element, args)
    elif args.element == '3DS':
        date_time = BJS.strftime('%Y%m%d')
        predict_3DS(path, ele_dir[args.element][args.type], date_time, args)
    else:
        date_time = BJS + datetime.timedelta(hours=-12)
        date_time_1 = date_time + datetime.timedelta(days=-1)
        date_time_1 = date_time_1.strftime('%Y%m%d')
        date_time_2 = date_time + datetime.timedelta(days=-2)
        date_time_2 = date_time_2.strftime('%Y%m%d')
        source_1 = os.path.join(date_time_1, ele_dir[args.element][args.type])
        source_2 = os.path.join(date_time_2, ele_dir[args.element][args.type])
        # predict_sst(path, ele_dir[args.element][args.type], date_time, args)
        if args.element == '3DT':
            predict_3DT(path, source_1, source_2, args)
        else:
            predict_elements(path, source_1, source_2, args.element, args)
elif args.mode == 'C':
    date_time = BJS + datetime.timedelta(hours=-12)
    date_time = date_time.strftime('%Y%m%d%H%M%S')
    date_folder = date_time[:8]
    hour = int(date_time[8:10])
    source = os.path.join(date_folder, ele_dir[args.element][args.type])
    bias_correction(path, source, hour, args)
