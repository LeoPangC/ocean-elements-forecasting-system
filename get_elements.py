import os.path
import numpy as np
import datetime
from class_combat_data import CombatData
from class_roll_prediction import RollPrediction
from utils import save_json, save_npy
from parameters import models_path, max_min, var_folder, mixture_vars, max_min_3D, NODATA


def predict_elements(path, raw_data_dir_1, raw_data_dir_2, element, args):
    # deg = 180.0 / np.pi
    ele_vars = mixture_vars[element]
    lat = list(map(float, args.lat.split(',')))
    lon = list(map(float, args.lon.split(',')))
    choose_region = {
        'south': lat[0],
        'north': lat[1],
        'west': lon[0],
        'east': lon[1],
        'step': float(args.resolution)
    }
    for vars_portion in ele_vars:
        dir_type = os.path.split(raw_data_dir_1)[-1]
        folder_name = var_folder[element][dir_type][vars_portion]
        raw_data_folder_1 = '/'.join([raw_data_dir_1, folder_name])
        raw_data_folder_2 = '/'.join([raw_data_dir_2, folder_name])

        # 7.10 更新，目前使用两天数据预测，使用15个时间步
        combatData_1 = CombatData(sub_folder=raw_data_folder_1,
                                  var_simple=vars_portion,
                                  absolute_path=path)
        combatData_1.trans_nc_to_npy(lat_lon=choose_region)
        predict_data_1 = combatData_1.get_npy()

        combatData_2 = CombatData(sub_folder=raw_data_folder_2,
                                  var_simple=vars_portion,
                                  absolute_path=path)

        combatData_2.trans_nc_to_npy(lat_lon=choose_region)
        predict_data_2 = combatData_2.get_npy()

        predict_data = np.concatenate([predict_data_2[1:], predict_data_1], axis=0)
        if element == 'sst':
            average = np.mean(predict_data[predict_data != -32767.0])
            predict_data[predict_data == -32767.0] = average
            predict_data = predict_data - 273.15
        var_prediction = RollPrediction(var_simple=vars_portion,
                                        absolute_path=path,
                                        model=models_path['_'.join([vars_portion, args.region])],
                                        region=args.region,
                                        split_num=15,
                                        data_max=max_min[args.region][vars_portion]['max'],
                                        data_min=max_min[args.region][vars_portion]['min'])
        var_prediction.data_pre_process(predict_data)

        for i in range(40):
            var_prediction.predict_elements()
            var_prediction.save_asc(str((i + 1) * 3), lon[0], lat[0], choose_region['step'], args.date[:8],
                                    nodata=NODATA[args.element])
            var_prediction.save_npy(str((i + 1) * 3), args.date[:8])
            var_prediction.post_process()
    return var_prediction.get_predict_result()


def predict_sal(path, folder, date, element, args):
    predict_data = np.array([])
    lat = [1.95, 25.95]
    lon = [98.95, 122.95]
    choose_region = {
        'south': lat[0],
        'north': lat[1],
        'west': lon[0],
        'east': lon[1],
        'step': float(args.resolution)
    }

    date_time = datetime.datetime.strptime(date, '%Y%m%d')
    for day in range(15):
        date_time = date_time + datetime.timedelta(days=-1)
        date_time = date_time.strftime('%Y%m%d')

        combatData = CombatData(sub_folder=os.path.join(date_time, folder),
                                var_simple=element,
                                region=args.region,
                                absolute_path=path)
        combatData.trans_nc_to_npy(lat_lon=choose_region)
        npy_data = combatData.get_npy()
        average = np.mean(npy_data[npy_data != -32767.0])
        npy_data[npy_data == -32767.0] = average

        try:
            predict_data = np.concatenate((npy_data, predict_data))
        except (UnboundLocalError, ValueError):
            predict_data = npy_data


        date_time = datetime.datetime.strptime(date_time, '%Y%m%d')

    # try:

    # except (OSError, KeyError, IndexError):
    #     combatData.trans_grb_to_npy(lat=(choose_region['south'], choose_region['north']),
    #                                 lon=(choose_region['west'], choose_region['east']))


    rollPrediction = RollPrediction(var_simple=element,
                                    absolute_path=path,
                                    model=models_path['_'.join([element, args.region])],
                                    region=args.region,
                                    split_num=15,
                                    data_max=max_min[args.region][element]['max'],
                                    data_min=max_min[args.region][element]['min'])
    rollPrediction.data_pre_process(predict_data)
    # 预测天数
    for i in range(5):
        rollPrediction.predict_elements()
        rollPrediction.save_asc(str((i + 1) * 3), lon[0], lat[0], choose_region['step'], args.date[:8],
                                nodata=NODATA[element])
        rollPrediction.save_npy(str((i + 1) * 3), args.date[:8])
        rollPrediction.post_process()

    return rollPrediction.get_predict_result()


def bias_correction(path, raw_data_dir, hour, args):
    predict_data = np.array([])
    ele_vars = mixture_vars[args.element]
    # raw_data_folder路径问题如何修改
    lat = list(map(float, args.lat.split(',')))
    lon = list(map(float, args.lon.split(',')))
    choose_region = {
        'south': lat[0],
        'north': lat[1],
        'west': lon[0],
        'east': lon[1],
        'step': float(args.resolution)
    }
    for vars_portion in ele_vars:

        dir_type = os.path.split(raw_data_dir)[-1]
        folder_name = var_folder[args.element][dir_type][vars_portion]
        raw_data_folder = '/'.join([raw_data_dir, folder_name])

        combatData = CombatData(sub_folder=raw_data_folder,
                                var_simple=vars_portion,
                                absolute_path=path)
        combatData.trans_nc_to_npy_one(lat_lon=choose_region, hour=hour)
        npy_data = combatData.get_npy()
        try:
            predict_data = np.concatenate((predict_data, npy_data))
        except (UnboundLocalError, ValueError):
            predict_data = npy_data

    for bc_var in ele_vars:
        if bc_var == 'v10':
            predict_data = np.flip(predict_data, axis=0)
        var_prediction = RollPrediction(var_simple=bc_var,
                                        absolute_path=path,
                                        model=models_path['bc_' + bc_var],
                                        region=args.region,
                                        split_num=15,
                                        data_max=max_min[args.region][bc_var]['max'],
                                        data_min=max_min[args.region][bc_var]['min'])
        var_prediction.data_pre_process(predict_data,
                                        mode=args.mode,
                                        bc_max=max_min[args.region]['bc_'+bc_var]['max'],
                                        bc_min=max_min[args.region]['bc_'+bc_var]['min'])
        var_prediction.predict_elements()
        var_prediction.save_asc('bc_' + bc_var, lon[0], lat[0], choose_region['step'], args.date[:8], args.date[8:10], args.mode)
        var_prediction.save_npy('bc_' + bc_var, args.date[:8])


def predict_3DT(path, raw_data_dir_1, raw_data_dir_2, args):
    # raw_data_folder路径问题如何修改
    lat = list(map(float, args.lat.split(',')))
    lon = list(map(float, args.lon.split(',')))
    choose_region = {
        'south': lat[0],
        'north': lat[1],
        'west': lon[0],
        'east': lon[1],
        'step': float(args.resolution)
    }

    result_3d = predict_elements(path, raw_data_dir_1[:-2]+'ERA5', raw_data_dir_2[:-2]+'ERA5', 'sst', args)
    model_folder = os.path.join(path, 'models', models_path[args.element])
    model_list = os.listdir(model_folder)
    model_list.sort()
    for i, model in enumerate(model_list):
        dir_type = os.path.split(raw_data_dir_1)[-1]
        folder_name = var_folder[args.element][dir_type][args.element]
        raw_data_folder_1 = '/'.join([raw_data_dir_1, folder_name])
        raw_data_folder_2 = '/'.join([raw_data_dir_2, folder_name])

        # 7.10 更新，目前使用两天数据预测，使用15个时间步
        combatData_1 = CombatData(sub_folder=raw_data_folder_1,
                                  var_simple=args.element,
                                  absolute_path=path)

        combatData_1.trans_nc_to_npy(lat_lon=choose_region, depth=i)
        predict_data_1 = combatData_1.get_npy()

        combatData_2 = CombatData(sub_folder=raw_data_folder_2,
                                  var_simple=args.element,
                                  absolute_path=path)

        combatData_2.trans_nc_to_npy(lat_lon=choose_region, depth=i)
        predict_data_2 = combatData_2.get_npy()

        predict_data = np.concatenate([predict_data_2[1:], predict_data_1], axis=0)
        var_prediction = RollPrediction(var_simple=args.element,
                                        absolute_path=path,
                                        model=os.path.join(models_path[args.element], model),
                                        region=args.region,
                                        split_num=15,
                                        data_max=max_min_3D[args.element][i]['max'],
                                        data_min=max_min_3D[args.element][i]['min'])

        var_prediction.data_pre_process(predict_data)
        for roll in range(40):
            var_prediction.predict_elements()
            var_prediction.post_process()
        predict_result = var_prediction.get_predict_result()
        predict_result[mask] = -32767.0
        if result_3d.shape[0] == 1:
            result_3d[mask] = -32767.0
        result_3d = np.concatenate((result_3d, predict_result))
    save_json(path, result_3d, '0', args.date[:8], args.element)
    save_npy(path, result_3d, '0', args.date[:8], args.element)


def predict_3DS(path, folder, date, args):
    predict_data = np.array([])
    lat = [1.95, 25.95]
    lon = [98.95, 122.95]
    choose_region = {
        'south': lat[0],
        'north': lat[1],
        'west': lon[0],
        'east': lon[1],
        'step': float(args.resolution)
    }

    surface_sal = predict_sal(path, folder, date, 'sss', args)
    result_3d = surface_sal
    model_folder = os.path.join(path, 'models', models_path[args.element])
    model_list = os.listdir(model_folder)
    model_list.sort()
    for i, model in enumerate(model_list):
        date_time = datetime.datetime.strptime(date, '%Y%m%d')
        for day in range(15):
            date_time = date_time + datetime.timedelta(days=-1)
            date_time = date_time.strftime('%Y%m%d')

            combatData = CombatData(sub_folder=os.path.join(date_time, folder),
                                    var_simple=args.element,
                                    region=args.region,
                                    absolute_path=path)
            combatData.trans_nc_to_npy(lat_lon=choose_region)
            npy_data = combatData.get_npy()
            mask = npy_data == -32767.0
            average = np.mean(npy_data[npy_data != -32767.0])
            npy_data[npy_data == -32767.0] = average
            try:
                predict_data = np.concatenate((npy_data, predict_data))
            except (UnboundLocalError, ValueError):
                predict_data = npy_data

            date_time = datetime.datetime.strptime(date_time, '%Y%m%d')

        var_prediction = RollPrediction(var_simple=args.element,
                                        absolute_path=path,
                                        model=os.path.join(models_path[args.element], model),
                                        region=args.region,
                                        split_num=15,
                                        data_max=max_min_3D[args.element][i]['max'],
                                        data_min=max_min_3D[args.element][i]['min'])

        var_prediction.data_pre_process(predict_data)
        for roll in range(5):
            var_prediction.predict_elements()
            var_prediction.post_process()
        predict_result = var_prediction.get_predict_result()
        predict_result[mask] = -32767.0
        if result_3d.shape[0] == 1:
            result_3d[mask] = -32767.0
        result_3d = np.concatenate((result_3d, predict_result))
    save_json(path, result_3d, '0', args.date[:8], args.element)
    save_npy(path, result_3d, '0', args.date[:8], args.element)