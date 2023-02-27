import os
import sys
from get_elements import predict_other_elements, predict_mixture


# 下面几个参数可以改成sys.argv[]获取外部参数
# argv = sys.argv[1]
# sub_sub_folder = os.path.split(argv)
# sub_folder = os.path.split(sub_sub_folder[0])
#
# path = os.path.split(os.path.split(sub_folder[0])[0])[0]
# element = sys.argv[3]
# region_name = sys.argv[2]
# raw_data_folder = os.path.join(sub_folder[-1], sub_sub_folder[-1])

# 绝对路径
path = os.getcwd()
element = 'sst'
region_name = 'r1'
raw_data_folder = 'new/TEM'

if element == 'cur' or element == 'win':
    predict_mixture(path, region_name, raw_data_folder, element)
else:
    predict_other_elements(path, element, region_name, raw_data_folder)
