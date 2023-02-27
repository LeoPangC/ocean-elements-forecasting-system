import os.path
import numpy as np
from class_combat_data import CombatData
from class_roll_prediction import RollPrediction
from utils import get_lat_lon, draw_current_figs, save_figs
from parameters import lat_lon_cut, models_path, max_min, variables, region, var_folder, mixture_vars


def predict_mixture(path, region_name, raw_data_dir, element):
    deg = 180.0 / np.pi
    ele_vars = mixture_vars[element]
    # raw_data_folder路径问题如何修改
    for vars_portion in ele_vars:
        choose_region = region[vars_portion][region_name]
        element_region = lat_lon_cut[vars_portion][region_name]
        dir_type = os.path.split(raw_data_dir)[-1]
        folder_name = var_folder[element][dir_type][vars_portion]
        raw_data_folder = '/'.join([raw_data_dir, folder_name])

        combatData = CombatData(sub_folder=raw_data_folder,
                                var=variables[vars_portion],
                                var_simple=vars_portion,
                                region=region_name,
                                absolute_path=path)
        try:
            combatData.trans_nc_to_npy(lat_lon=element_region)
        except (OSError, KeyError, IndexError):
            combatData.trans_grb_to_npy(lat=(choose_region['south'], choose_region['north']),
                                        lon=(choose_region['west'], choose_region['east']))
        combatData.gen_npy()

    var_u_prediction = RollPrediction(split_num=8,
                                      absolute_path=path,
                                      var_simple=ele_vars[0],
                                      region=region_name,
                                      model=models_path['_'.join([ele_vars[0], region_name])],
                                      data_max=max_min[region_name][ele_vars[0]]['max'],
                                      data_min=max_min[region_name][ele_vars[0]]['min'])

    var_v_prediction = RollPrediction(split_num=8,
                                      absolute_path=path,
                                      var_simple=ele_vars[1],
                                      region=region_name,
                                      model=models_path['_'.join([ele_vars[1], region_name])],
                                      data_max=max_min[region_name][ele_vars[1]]['max'],
                                      data_min=max_min[region_name][ele_vars[1]]['min'])

    lat, lon = get_lat_lon(south=choose_region['south'],
                           north=choose_region['north'],
                           west=choose_region['west'],
                           east=choose_region['east'],
                           step=choose_region['step'])

    for i in range(4):
        var_u_prediction.predict_elements()
        var_v_prediction.predict_elements()
        var_u_result = var_u_prediction.get_predict_result()
        var_v_result = var_v_prediction.get_predict_result()
        var_sped = np.sqrt(np.square(var_u_result) + np.square(var_v_result))
        # cur_dir1 = np.mod(180.0 + np.arctan2(var_u_result, var_v_result), 360.0)
        # cur_dir2 = np.mod(270.0 - np.arctan2(var_v_result, var_u_result), 360.0)
        var_dir = 180.0 + np.arctan2(var_u_result, var_v_result) * deg
        draw_current_figs(lat, lon, var_sped[0], var_dir, var_u_result[0], var_v_result[0])
        save_figs(fig_name=str((i + 1)*3), absolute_path=path, region=region_name, var_simple=element)
        var_v_prediction.post_process()


def predict_other_elements(path, element, region_name, raw_data_folder):
    choose_region = region[element][region_name]
    element_region = lat_lon_cut[element][region_name]

    combatData = CombatData(sub_folder=raw_data_folder,
                            var=variables[element],
                            var_simple=element,
                            region=region_name,
                            absolute_path=path)

    try:
        combatData.trans_nc_to_npy(lat_lon=element_region)
    except (OSError, KeyError, IndexError):
        combatData.trans_grb_to_npy(lat=(choose_region['south'], choose_region['north']),
                                    lon=(choose_region['west'], choose_region['east']))

    combatData.gen_npy()

    rollPrediction = RollPrediction(split_num=8,
                                    absolute_path=path,
                                    var_simple=element,
                                    region=region_name,
                                    model=models_path['_'.join([element, region_name])],
                                    data_max=max_min[region_name][element]['max'],
                                    data_min=max_min[region_name][element]['min'])
    lat, lon = get_lat_lon(south=choose_region['south'],
                           north=choose_region['north'],
                           west=choose_region['west'],
                           east=choose_region['east'],
                           step=choose_region['step'])

    for i in range(4):
        rollPrediction.predict_elements()
        rollPrediction.pre_draw()
        rollPrediction.draw_figs(lat, lon)
        rollPrediction.save_figs(str((i + 1) * 3))
        rollPrediction.post_process()
