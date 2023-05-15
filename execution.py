import os
import argparse
from get_elements import predict_other_elements, predict_mixture

parser = argparse.ArgumentParser(description='Ocean-Elements-Forecasting-System')

parser.add_argument('--folder', type=str,  default=os.getcwd(), help='Absolute path')
parser.add_argument('--region', type=str, required=True, default='r1', help='Forecasting region')
parser.add_argument('--element', type=str, required=True, default='sst', help='Ocean elements')
parser.add_argument('--type', type=str, required=True, default='uc', help='data type, options:[uc, grb]')
parser.add_argument('--mode', type=str, required=True, default='T', help='Start-up mode, options:[T, F]')
parser.add_argument('--source', type=str, default='new/Uc/TEM', help='data type, options:[uc, grb]')
parser.add_argument('--lat', type=str, default='15,18.5', help='Latitude')
parser.add_argument('--lon', type=str, default='111.5,115', help='Longitude')
parser.add_argument('--resolution', type=str, default='0.1', help='Resolution')

args = parser.parse_args()

if args.mode == 'F':
    argv = args.folder
    sub_sub_folder = os.path.split(argv)
    sub_folder = os.path.split(sub_sub_folder[0])
    folder = os.path.split(sub_folder[0])
    args.folder = os.path.split(os.path.split(folder[0])[0])[0]
    args.source = os.path.join(folder[-1], sub_folder[-1], sub_sub_folder[-1])

if args.element == 'cur' or args.element == 'win':
    predict_mixture(args.folder, args.region, args.source, args.element)
else:
    predict_other_elements(args.folder, args.element, args.region, args.source)
