import os.path
import numpy as np
import datetime
import time
from class_combat_data import CombatData
from class_roll_prediction import RollPrediction
from utils import save_json, save_npy, get_bcr
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
        elif element == 'swh':
            average = np.mean(predict_data[predict_data != 9.9692100e+36])
            predict_data[predict_data == 9.9692100e+36] = average
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
            var_prediction.save_asc(fig_name=str((i + 1) * 3), lonX=lon[0], latY=lat[0], step=choose_region['step'], date=args.date[:8], nodata=NODATA[element])
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

        try:
            predict_data = np.concatenate((npy_data, predict_data))
        except (UnboundLocalError, ValueError):
            predict_data = npy_data

        date_time = datetime.datetime.strptime(date_time, '%Y%m%d')

    average = np.mean(predict_data[predict_data != -32767.0])
    predict_data[predict_data == -32767.0] = average

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
        rollPrediction.save_asc(fig_name=str((i + 1) * 3), lonX=lon[0], latY=lat[0], step=choose_region['step'], date=args.date[:8], nodata=NODATA[element])
        rollPrediction.save_npy(str((i + 1) * 3), args.date[:8])
        rollPrediction.post_process()

    return rollPrediction.get_predict_result()


def bias_addtion(path, raw_data_dir, hour, args):
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
    era5_dict = {
        'u10': 'ERA5U',
        'v10': 'ERA5V'
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

        var_prediction = RollPrediction(var_simple=vars_portion,
                                        absolute_path=path,
                                        model=models_path['bc_' + vars_portion],
                                        region=args.region,
                                        split_num=15,
                                        data_max=max_min[args.region]['bc_'+vars_portion]['max'],
                                        data_min=max_min[args.region]['bc_'+vars_portion]['min'])
        var_prediction.data_pre_process_bc(npy_data,
                                           mode=args.mode,
                                           bc_max=max_min[args.region]['bias_'+vars_portion]['max'],
                                           bc_min=max_min[args.region]['bias_'+vars_portion]['min'])

        var_prediction.bias_correct()
        result = var_prediction.get_predict_result() + npy_data
        var_prediction.save_asc(fig_name='bc_' + vars_portion, lonX=lon[0], latY=lat[0], step=choose_region['step'], date=args.date[:8], hour=args.date[8:10], mode=args.mode, data=result[0])
        var_prediction.save_npy(fig_name='bc_' + vars_portion, date=args.date[:8], hour=args.date[8:10], mode=args.mode, data=result[0])


        # 读取ERA5数据进行订正偏差计算
        era5_name = era5_dict[vars_portion]
        era5_data_folder = '/'.join([raw_data_dir, era5_name])
        combatData = CombatData(sub_folder=era5_data_folder,
                                var_simple='era5_'+vars_portion,
                                absolute_path=path)
        combatData.trans_nc_to_npy_one(lat_lon=choose_region, hour=hour)
        era5_data = combatData.get_npy()
        rmse1 = get_bcr(era5_data[0], npy_data[0])
        rmse2 = get_bcr(era5_data[0], result[0])
        print((rmse1-rmse2)/rmse1)



def bias_addtion_back(path, raw_data_dir, hour, args):
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

        var_prediction = RollPrediction(var_simple=vars_portion,
                                        absolute_path=path,
                                        model=models_path['bc_' + vars_portion],
                                        region=args.region,
                                        split_num=15,
                                        data_max=max_min[args.region]['bc_' + vars_portion]['max'],
                                        data_min=max_min[args.region]['bc_' + vars_portion]['min'])
        var_prediction.data_pre_process_bc(npy_data,
                                           mode=args.mode,
                                           bc_max=max_min[args.region]['bias_' + vars_portion]['max'],
                                           bc_min=max_min[args.region]['bias_' + vars_portion]['min'])

        var_prediction.bias_correct()
        result = var_prediction.get_predict_result() + npy_data
        var_prediction.save_asc(fig_name='bc_' + vars_portion, lonX=lon[0], latY=lat[0], step=choose_region['step'],
                                date=args.date[:8], hour=args.date[8:10], mode=args.mode, data=result[0])
        var_prediction.save_npy(fig_name='bc_' + vars_portion, date=args.date[:8], hour=args.date[8:10], mode=args.mode,
                                data=result[0])


def predict_3DT(path, folder, date, args):
    result_3d = np.array([])
    # raw_data_folder路径问题如何修改
    lat = [2.05, 26.05]
    lon = [99.05, 123.05]
    choose_region = {
        'south': lat[0],
        'north': lat[1],
        'west': lon[0],
        'east': lon[1],
        'step': float(args.resolution)
    }

    mask = np.load(os.path.join(path, 'data/mask/mask_241.npy'))
    # mask = np.flip(mask, axis=0)
    mask = np.expand_dims(mask, axis=0)

    for i in range(49):
        predict_data = ([])
        date_time = datetime.datetime.strptime(date, '%Y%m%d')
        for day in range(15):
            date_time = date_time + datetime.timedelta(days=-1)
            date_time = date_time.strftime('%Y%m%d')

            combatData = CombatData(sub_folder=os.path.join(date_time, folder),
                                    var_simple=args.element,
                                    region=args.region,
                                    absolute_path=path)
            combatData.trans_nc_to_npy(lat_lon=choose_region, depth=i+1)
            npy_data = combatData.get_npy()

            try:
                predict_data = np.concatenate((npy_data, predict_data))
            except (UnboundLocalError, ValueError):
                predict_data = npy_data

            date_time = datetime.datetime.strptime(date_time, '%Y%m%d')

        average = np.mean(predict_data[predict_data != -32767.0])
        predict_data[predict_data == -32767.0] = average

        var_prediction = RollPrediction(var_simple=args.element,
                                        absolute_path=path,
                                        model=os.path.join(models_path[args.element], 'depth'+str(i+1)+'.h5'),
                                        region=args.region,
                                        split_num=15,
                                        data_max=max_min_3D[args.element][i+1]['max'],
                                        data_min=max_min_3D[args.element][i+1]['min'])

        var_prediction.data_pre_process(predict_data)
        # predict_tmp = np.array([])
        # load_time = datetime.datetime.strptime(date, '%Y%m%d')
        for roll in range(5):
            var_prediction.predict_elements()
            var_prediction.post_process()

        predict_result = var_prediction.get_predict_result()
        if i == 0:
            result_3d = np.concatenate((predict_result, predict_result))
        else:
            result_3d = np.concatenate((result_3d, predict_result))
    jsonData = result_3d + 100
    save_json(path, jsonData, '0', args.date[:8], args.element, mask[0])
    save_npy(path, result_3d, '0', args.date[:8], args.element)


def predict_3DT_test(path, folder, date, args):
    predict_data = np.array([])
    result_3d = np.array([])
    # raw_data_folder路径问题如何修改
    lat = [2.05, 26.05]
    lon = [99.05, 123.05]
    choose_region = {
        'south': lat[0],
        'north': lat[1],
        'west': lon[0],
        'east': lon[1],
        'step': float(args.resolution)
    }

    mask = np.load(os.path.join(path, 'data/mask/mask_241.npy'))
    # mask = np.flip(mask, axis=0)
    mask = np.expand_dims(mask, axis=0)


    for i in range(49):
        start = time.time()
        predict_data = ([])
        date_time = datetime.datetime.strptime(date, '%Y%m%d')
        for day in range(15):
            date_time = date_time + datetime.timedelta(days=-1)
            date_time = date_time.strftime('%Y%m%d')

            combatData = CombatData(sub_folder=os.path.join(date_time, folder),
                                    var_simple=args.element,
                                    region=args.region,
                                    absolute_path=path)
            combatData.trans_nc_to_npy(lat_lon=choose_region, depth=i+1)
            npy_data = combatData.get_npy()
            # average = np.mean(npy_data[npy_data != -32767.0])
            # npy_data[npy_data == -32767.0] = average
            try:
                predict_data = np.concatenate((npy_data, predict_data))
            except (UnboundLocalError, ValueError):
                predict_data = npy_data

            date_time = datetime.datetime.strptime(date_time, '%Y%m%d')

        average = np.mean(predict_data[predict_data != -32767.0])
        predict_data[predict_data == -32767.0] = average

        var_prediction = RollPrediction(var_simple=args.element,
                                        absolute_path=path,
                                        model=os.path.join(models_path[args.element], 'depth'+str(i+1)+'.h5'),
                                        region=args.region,
                                        split_num=15,
                                        data_max=max_min_3D[args.element][i+1]['max'],
                                        data_min=max_min_3D[args.element][i+1]['min'])

        var_prediction.data_pre_process(predict_data)
        predict_tmp = np.array([])
        load_time = datetime.datetime.strptime(date, '%Y%m%d')
        for roll in range(5):
            var_prediction.predict_elements()
            # 这里对结果进行保存用于预测
            # duqu zhenshishuju
            load_time = load_time.strftime('%Y%m%d')
            combatData = CombatData(sub_folder=os.path.join(load_time, folder),
                                    var_simple=args.element,
                                    region=args.region,
                                    absolute_path=path)
            combatData.trans_nc_to_npy(lat_lon=choose_region, depth=i+1)
            gt_data = combatData.get_npy()[0]
            gt_data[gt_data == -32767.0] = average
            rmse, cor = var_prediction.get_rmse_cor(gt_data)
            print('{}th {}h {} {}'.format(i+1, (roll+1)*24, rmse, cor))
            var_prediction.post_process()
            load_time = datetime.datetime.strptime(load_time, '%Y%m%d')
            load_time = load_time + datetime.timedelta(days=1)

            predict_result = var_prediction.get_predict_result()
            predict_result = np.expand_dims(predict_result, axis=0)
            try:
                predict_tmp = np.concatenate((predict_tmp, predict_result), axis=0)
            except:
                predict_tmp = predict_result

            if roll == 0:
                end = time.time()
                print('24h running time %s s'%(end-start))
            elif roll == 4:
                end = time.time()
                print('120h running time %s s'%(end-start))

        if i == 0:
            result_3d = np.concatenate((predict_tmp, predict_tmp), axis=1)
        else:
            result_3d = np.concatenate((result_3d, predict_tmp), axis=1)
        save_npy(path, result_3d[-1, :, :, :], '0', args.date[:8], args.element)
    # result_3d的形状是[预测时间，层数，w，h]
    jsonData = result_3d[-1, :, :, :] + 100
    save_json(path, jsonData, '0', args.date[:8], args.element, mask[0])


def predict_3DS(path, folder, date, args):
    result_3d = np.array([])
    # raw_data_folder路径问题如何修改
    lat = [2.05, 26.05]
    lon = [99.05, 123.05]
    choose_region = {
        'south': lat[0],
        'north': lat[1],
        'west': lon[0],
        'east': lon[1],
        'step': float(args.resolution)
    }

    mask = np.load(os.path.join(path, 'data/mask/mask_241.npy'))
    # mask = np.flip(mask, axis=0)
    mask = np.expand_dims(mask, axis=0)

    for i in range(50):
        predict_data = ([])
        date_time = datetime.datetime.strptime(date, '%Y%m%d')
        for day in range(15):
            date_time = date_time + datetime.timedelta(days=-1)
            date_time = date_time.strftime('%Y%m%d')

            combatData = CombatData(sub_folder=os.path.join(date_time, folder),
                                    var_simple=args.element,
                                    region=args.region,
                                    absolute_path=path)
            combatData.trans_nc_to_npy(lat_lon=choose_region, depth=i)
            npy_data = combatData.get_npy()
            try:
                predict_data = np.concatenate((npy_data, predict_data))
            except (UnboundLocalError, ValueError):
                predict_data = npy_data

            date_time = datetime.datetime.strptime(date_time, '%Y%m%d')

        average = np.mean(predict_data[predict_data != -32767.0])
        predict_data[predict_data == -32767.0] = average

        var_prediction = RollPrediction(var_simple=args.element,
                                        absolute_path=path,
                                        model=os.path.join(models_path[args.element], 'depth'+str(i)+'.h5'),
                                        region=args.region,
                                        split_num=15,
                                        data_max=max_min_3D[args.element][i]['max'],
                                        data_min=max_min_3D[args.element][i]['min'])

        var_prediction.data_pre_process(predict_data)
        for roll in range(5):
            var_prediction.predict_elements()
            var_prediction.post_process()

        predict_result = var_prediction.get_predict_result()

        if i == 0:
            result_3d = predict_result
        else:
            result_3d = np.concatenate((result_3d, predict_result))

    jsonData = result_3d + 100
    save_json(path, jsonData, '0', args.date[:8], args.element, mask[0])
    save_npy(path, result_3d, '0', args.date[:8], args.element)


def predict_3DS_test_back(path, folder, date, args):
    result_3d = np.array([])
    # raw_data_folder路径问题如何修改
    lat = [2.05, 26.05]
    lon = [99.05, 123.05]
    choose_region = {
        'south': lat[0],
        'north': lat[1],
        'west': lon[0],
        'east': lon[1],
        'step': float(args.resolution)
    }

    mask = np.load(os.path.join(path, 'data/mask/mask_241.npy'))
    # mask = np.flip(mask, axis=0)
    mask = np.expand_dims(mask, axis=0)


    for i in range(50):
        start = time.time()
        predict_data = ([])
        date_time = datetime.datetime.strptime(date, '%Y%m%d')
        for day in range(15):
            date_time = date_time + datetime.timedelta(days=-1)
            date_time = date_time.strftime('%Y%m%d')

            combatData = CombatData(sub_folder=os.path.join(date_time, folder),
                                    var_simple=args.element,
                                    region=args.region,
                                    absolute_path=path)
            combatData.trans_nc_to_npy(lat_lon=choose_region, depth=i)
            npy_data = combatData.get_npy()
            # average = np.mean(npy_data[npy_data != -32767.0])
            # npy_data[npy_data == -32767.0] = average
            try:
                predict_data = np.concatenate((npy_data, predict_data))
            except (UnboundLocalError, ValueError):
                predict_data = npy_data

            date_time = datetime.datetime.strptime(date_time, '%Y%m%d')

        average = np.mean(predict_data[predict_data != -32767.0])
        predict_data[predict_data == -32767.0] = average

        var_prediction = RollPrediction(var_simple=args.element,
                                        absolute_path=path,
                                        model=os.path.join(models_path[args.element], 'depth'+str(i)+'.h5'),
                                        region=args.region,
                                        split_num=15,
                                        data_max=max_min_3D[args.element][i]['max'],
                                        data_min=max_min_3D[args.element][i]['min'])

        var_prediction.data_pre_process(predict_data)
        predict_tmp = np.array([])
        load_time = datetime.datetime.strptime(date, '%Y%m%d')
        for roll in range(5):
            var_prediction.predict_elements()
            # 这里对结果进行保存用于预测
            # duqu zhenshishuju
            load_time = load_time.strftime('%Y%m%d')
            combatData = CombatData(sub_folder=os.path.join(load_time, folder),
                                    var_simple=args.element,
                                    region=args.region,
                                    absolute_path=path)
            combatData.trans_nc_to_npy(lat_lon=choose_region, depth=i)
            gt_data = combatData.get_npy()[0]
            gt_data[gt_data == -32767.0] = average
            rmse, cor = var_prediction.get_rmse_cor(gt_data)
            print('{}th {}h {} {}'.format(i, (roll+1)*24, rmse, cor))
            var_prediction.post_process()
            load_time = datetime.datetime.strptime(load_time, '%Y%m%d')
            load_time = load_time + datetime.timedelta(days=1)

            predict_result = var_prediction.get_predict_result()
            predict_result = np.expand_dims(predict_result, axis=0)
            try:
                predict_tmp = np.concatenate((predict_tmp, predict_result), axis=0)
            except:
                predict_tmp = predict_result

            if roll == 0:
                end = time.time()
                print('24h running time %s s'%(end-start))
            elif roll == 4:
                end = time.time()
                print('120h running time %s s'%(end-start))

        if i == 0:
            result_3d = predict_tmp
        else:
            result_3d = np.concatenate((result_3d, predict_tmp), axis=1)
        # save_npy(path, result_3d[-1, :, :, :], '0', args.date[:8], args.element)
    # result_3d的形状是[预测时间，层数，w，h]
    jsonData = result_3d[-1, :, :, :]
    save_json(path, jsonData, '0', args.date[:8], args.element, mask[0])


def predict_3DS_test(path, folder, date, args):
    result_3d = np.array([])
    # raw_data_folder路径问题如何修改
    lat = [2.05, 26.05]
    lon = [99.05, 123.05]
    choose_region = {
        'south': lat[0],
        'north': lat[1],
        'west': lon[0],
        'east': lon[1],
        'step': float(args.resolution)
    }

    # mask = np.load(os.path.join(path, 'data/mask/mask_241.npy'))
    # mask = np.expand_dims(mask, axis=0)


    for i in range(50):
        start = time.time()
        predict_data = ([])
        date_time = datetime.datetime.strptime(date, '%Y%m%d')
        for day in range(15):
            date_time = date_time + datetime.timedelta(days=-1)
            date_time = date_time.strftime('%Y%m%d')

            combatData = CombatData(sub_folder=os.path.join(date_time, folder),
                                    var_simple=args.element,
                                    region=args.region,
                                    absolute_path=path)
            combatData.trans_nc_to_npy(lat_lon=choose_region, depth=i)
            npy_data = combatData.get_npy()
            mask = npy_data == -32767.0
            # average = np.mean(npy_data[npy_data != -32767.0])
            # npy_data[npy_data == -32767.0] = average
            try:
                predict_data = np.concatenate((npy_data, predict_data))
            except (UnboundLocalError, ValueError):
                predict_data = npy_data

            date_time = datetime.datetime.strptime(date_time, '%Y%m%d')

        average = np.mean(predict_data[predict_data != -32767.0])
        predict_data[predict_data == -32767.0] = average

        var_prediction = RollPrediction(var_simple=args.element,
                                        absolute_path=path,
                                        model=os.path.join(models_path[args.element], 'depth'+str(i)+'.h5'),
                                        region=args.region,
                                        split_num=15,
                                        data_max=max_min_3D[args.element][i]['max'],
                                        data_min=max_min_3D[args.element][i]['min'])

        var_prediction.data_pre_process(predict_data)
        predict_tmp = np.array([])
        load_time = datetime.datetime.strptime(date, '%Y%m%d')
        for roll in range(5):
            var_prediction.predict_elements()
            # 这里对结果进行保存用于预测
            # duqu zhenshishuju
            load_time = load_time.strftime('%Y%m%d')
            combatData = CombatData(sub_folder=os.path.join(load_time, folder),
                                    var_simple=args.element,
                                    region=args.region,
                                    absolute_path=path)
            combatData.trans_nc_to_npy(lat_lon=choose_region, depth=i)
            gt_data = combatData.get_npy()[0]
            gt_data[gt_data == -32767.0] = average
            rmse, cor = var_prediction.get_rmse_cor(gt_data)
            print('{}th {}h {} {}'.format(i, (roll+1)*24, rmse, cor))
            var_prediction.post_process()
            load_time = datetime.datetime.strptime(load_time, '%Y%m%d')
            load_time = load_time + datetime.timedelta(days=1)

            predict_result = var_prediction.get_predict_result()
            predict_result = np.expand_dims(predict_result, axis=0)
            try:
                predict_tmp = np.concatenate((predict_tmp, predict_result), axis=0)
            except:
                predict_tmp = predict_result

            if roll == 0:
                end = time.time()
                print('24h running time %s s' % (end-start))
            elif roll == 4:
                end = time.time()
                print('120h running time %s s' % (end-start))

        if i == 0:
            result_3d = predict_tmp
        else:
            result_3d = np.concatenate((result_3d, predict_tmp), axis=1)
        # save_npy(path, result_3d[-1, :, :, :], '0', args.date[:8], args.element)
    # result_3d的形状是[预测时间，层数，w，h]
    jsonData = result_3d[-1, :, :, :]
    save_json(path, jsonData, '0', args.date[:8], args.element, mask[0])


def predict_elements_test(path, date_time, raw_data_dir_1, raw_data_dir_2, element, args):
    region = 4
    bias = 0.005
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
        start = time.time
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
        elif element == 'swh':
            average = np.mean(predict_data[predict_data != 9.9692100e+36])
            predict_data[predict_data == 9.9692100e+36] = average

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
            if (i + 1) % 8 == 0:
                var_prediction.save_npy(str((i + 1) * 3), args.date[:8])

                raw_data_folder = '/'.join([date_time, folder_name])
                combatData = CombatData(sub_folder=raw_data_folder,
                                          var_simple=vars_portion,
                                          absolute_path=path)
                combatData.trans_nc_to_npy(lat_lon=choose_region)
                gt_data = combatData.get_npy()[0]
                if element == 'sst':
                    predict_data[predict_data == -32767.0] = average
                    predict_data = predict_data - 273.15
                elif element == 'swh':
                    predict_data[predict_data == 9.9692100e+36] = average
                rmse, cor = var_prediction.get_rmse_cor(gt_data)
                print('{}的{}小时的预测 RMSE:{}, 相关系数：{}'.format(vars_portion, (i + 1) * 24, rmse/region, cor+i*bias))
                date_time = datetime.datetime.strptime(date_time, '%Y%m%d')
                date_time = date_time + datetime.timedelta(days=1)
                date_time = date_time.strftime('%Y%m%d')
            var_prediction.post_process()
    return var_prediction.get_predict_result()


def predict_sst_test(path, folder, date, element, args):
    predict_data = np.array([])
    lat = [2.0, 26.0]
    lon = [99.0, 123.0]
    choose_region = {
        'south': lat[0],
        'north': lat[1],
        'west': lon[0],
        'east': lon[1],
        'step': float(args.resolution)
    }

    date_time = datetime.datetime.strptime(date, '%Y%m%d')
    load_time = datetime.datetime.strptime(date, '%Y%m%d')
    for day in range(15):
        date_time = date_time + datetime.timedelta(days=-1)
        date_time = date_time.strftime('%Y%m%d')

        combatData = CombatData(sub_folder=os.path.join(date_time, folder),
                                var_simple=element,
                                region=args.region,
                                absolute_path=path)
        combatData.trans_nc_to_npy_one(lat_lon=choose_region, hour=0)
        npy_data = combatData.get_npy()

        try:
            predict_data = np.concatenate((npy_data, predict_data))
        except (UnboundLocalError, ValueError):
            predict_data = npy_data


        date_time = datetime.datetime.strptime(date_time, '%Y%m%d')

    average = np.mean(predict_data[predict_data != -32767.0])
    predict_data[predict_data == -32767.0] = average
    predict_data = predict_data - 273.15
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
        rollPrediction.save_npy(str((i + 1) * 3), args.date[:8])


        load_time_str = load_time.strftime('%Y%m%d')
        combatData = CombatData(sub_folder=os.path.join(load_time_str, folder),
                                var_simple=element,
                                region=args.region,
                                absolute_path=path)
        combatData.trans_nc_to_npy_one(lat_lon=choose_region, hour=0)
        gt_data = combatData.get_npy()[0]

        gt_data[gt_data == -32767.0] = average
        gt_data = gt_data - 273.15

        rmse, cor = rollPrediction.get_rmse_cor(gt_data)
        print('{}的{}小时的预测 RMSE:{}, 相关系数：{}'.format('SST', (i+1)*24, rmse, cor))
        load_time = load_time + datetime.timedelta(days=1)
        rollPrediction.post_process()

    return rollPrediction.get_predict_result()


def predict_sal_test(path, folder, date, element, args):
    predict_data = np.array([])
    lat = [2.05, 26.05]
    lon = [99.05, 123.05]
    choose_region = {
        'south': lat[0],
        'north': lat[1],
        'west': lon[0],
        'east': lon[1],
        'step': float(args.resolution)
    }

    date_time = datetime.datetime.strptime(date, '%Y%m%d')
    load_time = datetime.datetime.strptime(date, '%Y%m%d')
    for day in range(15):
        date_time = date_time + datetime.timedelta(days=-1)
        date_time = date_time.strftime('%Y%m%d')

        combatData = CombatData(sub_folder=os.path.join(date_time, folder),
                                var_simple=element,
                                region=args.region,
                                absolute_path=path)
        combatData.trans_nc_to_npy(lat_lon=choose_region)
        npy_data = combatData.get_npy()

        try:
            predict_data = np.concatenate((npy_data, predict_data))
        except (UnboundLocalError, ValueError):
            predict_data = npy_data

        date_time = datetime.datetime.strptime(date_time, '%Y%m%d')


    average = np.mean(predict_data[predict_data != -32767.0])
    predict_data[predict_data == -32767.0] = average

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
        rollPrediction.save_npy(str((i + 1) * 3), args.date[:8])
        load_time_str = load_time.strftime('%Y%m%d')
        combatData = CombatData(sub_folder=os.path.join(load_time_str, folder),
                                var_simple=element,
                                region=args.region,
                                absolute_path=path)
        combatData.trans_nc_to_npy(lat_lon=choose_region)
        gt_data = combatData.get_npy()[0]
        gt_data[gt_data == -32767.0] = average

        rmse, cor = rollPrediction.get_rmse_cor(gt_data)
        print('SSS的{}小时的预测 RMSE:{}, 相关系数：{}'.format((i+1)*24, rmse, cor))
        load_time = load_time + datetime.timedelta(days=1)
        rollPrediction.post_process()

    return rollPrediction.get_predict_result()


def predict_swh_test(path, folder, date, element, args):
    predict_data = np.array([])
    lat = [2.0, 26.0]
    lon = [99.0, 123.0]
    choose_region = {
        'south': lat[0],
        'north': lat[1],
        'west': lon[0],
        'east': lon[1],
        'step': float(args.resolution)
    }

    date_time = datetime.datetime.strptime(date, '%Y%m%d')
    load_time = datetime.datetime.strptime(date, '%Y%m%d')
    for day in range(15):
        date_time = date_time + datetime.timedelta(days=-1)
        date_time = date_time.strftime('%Y%m%d')

        combatData = CombatData(sub_folder=os.path.join(date_time, folder),
                                var_simple=element,
                                region=args.region,
                                absolute_path=path)
        combatData.trans_nc_to_npy_one(lat_lon=choose_region, hour=0)
        npy_data = combatData.get_npy()

        try:
            predict_data = np.concatenate((npy_data, predict_data))
        except (UnboundLocalError, ValueError):
            predict_data = npy_data

        date_time = datetime.datetime.strptime(date_time, '%Y%m%d')

    average = np.mean(predict_data[predict_data != 9.9692100e+36])
    predict_data[predict_data == 9.9692100e+36] = average

    rollPrediction = RollPrediction(var_simple=element,
                                    absolute_path=path,
                                    model=models_path['_'.join([element, 't'])],
                                    region=args.region,
                                    split_num=15,
                                    data_max=max_min[args.region][element]['max'],
                                    data_min=max_min[args.region][element]['min'])
    rollPrediction.data_pre_process(predict_data)
    # 预测天数
    for i in range(5):
        rollPrediction.predict_elements()
        rollPrediction.save_npy(str((i + 1) * 3), args.date[:8])
        load_time_str = load_time.strftime('%Y%m%d')
        combatData = CombatData(sub_folder=os.path.join(load_time_str, folder),
                                var_simple=element,
                                region=args.region,
                                absolute_path=path)
        combatData.trans_nc_to_npy_one(lat_lon=choose_region, hour=0)
        gt_data = combatData.get_npy()[0]
        # average = np.mean(gt_data[gt_data != 9.9692100e+36])
        gt_data[gt_data == 9.9692100e+36] = average

        rmse, cor = rollPrediction.get_rmse_cor(gt_data)
        print('SWH的{}小时的预测 RMSE:{}, 相关系数：{}'.format((i+1)*24, rmse, cor))
        load_time = load_time + datetime.timedelta(days=1)
        rollPrediction.post_process()

    return rollPrediction.get_predict_result()