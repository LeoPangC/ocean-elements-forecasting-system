import os.path
import numpy as np
import datetime
from class_combat_data import CombatData
from class_roll_prediction import RollPrediction
from utils import save_json
from parameters import models_path, max_min, var_folder, mixture_vars, max_min_3D


def predict_elements(path, raw_data_dir_1, raw_data_dir_2, args):
    # deg = 180.0 / np.pi
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
        dir_type = os.path.split(raw_data_dir_1)[-1]
        folder_name = var_folder[args.element][dir_type][vars_portion]
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
        if args.element == 'sst':
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
            var_prediction.save_asc(str((i + 1) * 3), lon[0], lat[0], choose_region['step'], args.date[:8])
            # pred_u.append(var_prediction.get_predict_result()[0])
            var_prediction.post_process()


def predict_sal(path, folder, date, args):
    predict_data = np.array([])
    lat = list(map(float, args.lat.split(',')))
    lon = list(map(float, args.lon.split(',')))
    choose_region = {
        'south': lat[0],
        'north': lat[1],
        'west': lon[0],
        'east': lon[1],
        'step': float(args.resolution)
    }
    # element_region = lat_lon_cut[args.element][args.region]
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


    rollPrediction = RollPrediction(var_simple=args.element,
                                    absolute_path=path,
                                    model=models_path['_'.join([args.element, args.region])],
                                    region=args.region,
                                    split_num=15,
                                    data_max=max_min[args.region][args.element]['max'],
                                    data_min=max_min[args.region][args.element]['min'])
    rollPrediction.data_pre_process(predict_data)
    # 预测天数
    for i in range(5):
        rollPrediction.predict_elements()
        rollPrediction.save_asc(str((i + 1) * 3), lon[0], lat[0], choose_region['step'], args.date[:8])
        rollPrediction.post_process()


def predict_sst(path, folder, date, args):
    predict_data = np.array([])
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

    date_time = datetime.datetime.strptime(date, '%Y%m%d')
    for day in range(2):
        date_time = date_time + datetime.timedelta(days=-1)
        date_time = date_time.strftime('%Y%m%d')

        root_dir = os.path.join(path, 'data', 'raw_data', os.path.join(date_time, folder))
        data_files = [file for file in os.listdir(root_dir)]
        for file in data_files:
            npy_data = np.load(os.path.join(root_dir, file))
            npy_data = npy_data[4:-4, 28:-28]
            npy_data = np.flip(npy_data, axis=0)
            # era5 无效数据替换为平均数据
            average = np.mean(npy_data[npy_data != -32767.0])
            npy_data[npy_data == -32767.0] = average
            npy_data = npy_data - 273.15
            npy_data = np.expand_dims(npy_data, axis=0)
            try:
                predict_data = np.concatenate((predict_data, npy_data))
            except (UnboundLocalError, ValueError):
                predict_data = npy_data

        date_time = datetime.datetime.strptime(date_time, '%Y%m%d')

    predict_data = predict_data[:15]
    var_prediction = RollPrediction(var_simple=args.element,
                                    absolute_path=path,
                                    model=models_path['_'.join([args.element, args.region])],
                                    region=args.region,
                                    split_num=15,
                                    data_max=max_min[args.region][args.element]['max'],
                                    data_min=max_min[args.region][args.element]['min'])

    var_prediction.data_pre_process(predict_data)
    for i in range(4):
        var_prediction.predict_elements()
        var_prediction.save_asc(str((i + 1) * 3), lon[0], lat[0], choose_region['step'], args.date[:8])
        var_prediction.post_process()


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


def predict_3DT(path, raw_data_dir_1, raw_data_dir_2, args):
    result_3d = np.array([])
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
        var_prediction.predict_elements()
        predict_result = var_prediction.get_predict_result()
        try:
            result_3d = np.concatenate((result_3d, predict_result))
        except (UnboundLocalError, ValueError):
            result_3d = predict_result
    save_json(path, result_3d, '0', args.date[:8], args.element)


def predict_3DS(path, folder, date, args):
    predict_data = np.array([])
    lat = list(map(float, args.lat.split(',')))
    lon = list(map(float, args.lon.split(',')))
    choose_region = {
        'south': lat[0],
        'north': lat[1],
        'west': lon[0],
        'east': lon[1],
        'step': float(args.resolution)
    }

    date_time = datetime.datetime.strptime(date, '%Y%m%d')
    model_folder = os.path.join(path, 'models', models_path[args.element])
    model_list = os.listdir(model_folder)
    model_list.sort()
    for i, model in enumerate(model_list):
        for day in range(15):
            date_time = date_time + datetime.timedelta(days=-1)
            date_time = date_time.strftime('%Y%m%d')

            combatData = CombatData(sub_folder=os.path.join(date_time, folder),
                                    var_simple=args.element,
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

        var_prediction = RollPrediction(var_simple=args.element,
                                        absolute_path=path,
                                        model=os.path.join(models_path[args.element], model),
                                        region=args.region,
                                        split_num=15,
                                        data_max=max_min[args.element][i]['max'],
                                        data_min=max_min[args.element][i]['min'])

        var_prediction.data_pre_process(predict_data)
        var_prediction.predict_elements()
        var_prediction.get_predict_result()[0]