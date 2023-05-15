models_path = {
    'u10_r1': 'u10/u10_r1_single_ConvLSTM_u__single_ConvLSTM_s_e100.h5',
    'v10_r1': 'v10/v10_r1_single_ConvLSTM_u__single_ConvLSTM_s_e100.h5',
    'u10_r2': 'u10/u10_r2_single_ConvLSTM_u__single_ConvLSTM_s_e100.h5',
    'v10_r2': 'v10/v10_r2_single_ConvLSTM_u__single_ConvLSTM_s_e100.h5',
    'swh_r1': 'swh/swh_r1_single_ConvLSTM_u__single_ConvLSTM_s_e100.h5',
    'swh_r2': 'swh/swh_r2_single_ConvLSTM_u__single_ConvLSTM_s_e100.h5',
    'wu_r1': 'w_u/w_u_r1_U_current.h5',
    'wu_r2': 'w_u/w_u_r2_U_current.h5',
    'wv_r1': 'w_v/w_v_r1_V_current.h5',
    'wv_r2': 'w_v/w_v_r2_V_current.h5',
    'sst_r1': 'sst/sst_r1_single_ConvLSTM_u__single_ConvLSTM_s_e100.h5',
    'sst_r2': 'sst/sst_r2_single_ConvLSTM_u__single_ConvLSTM_s_e100.h5',
    'sss_r1': 'sss/sss_r1_single_ConvLSTM_u__single_ConvLSTM_s_e100.h5',
    'sss_r2': 'sss/sss_r2_single_ConvLSTM_u__single_ConvLSTM_s_e100.h5'
}

# sst和sss的两种数据未知
lat_lon_cut = {
    'u10': {
        'r1': [
            {
                'lat': (194, 209),
                'lon': (346, 361),
                'step': 1
            }
        ],
        'r2': [
            {
                'lat': (198, 213),
                'lon': (366, 381),
                'step': 1
            }
        ]
    },
    'v10': {
        'r1': [
            {
                'lat': (194, 209),
                'lon': (346, 361),
                'step': 1
            }
        ],
        'r2': [
            {
                'lat': (198, 213),
                'lon': (366, 381),
                'step': 1
            }
        ]
    },
    'swh': {
        'r1': [
            {
                'lat': (485, 521),
                'lon': (865, 901),
                'step': 5
            },
            {
               'lat': (935, 971),
               'lon': (1165, 1201),
               'step': 5
            }
        ],
        'r2': [
            {
                'lat': (495, 531),
                'lon': (915, 951),
                'step': 5
            },
            {
                'lat': (945, 981),
                'lon': (1215, 1251),
                'step': 5
            }
        ]
    },
    'wu': {
        'r1': [
            {
                'lat': (0, 36),
                'lon': (55, 91),
                'step': 1
            },
            {
                'lat': (900, 936),
                'lon': (1105, 1141),
                'step': 1
            }
        ],
        'r2': [
            {
                'lat': (30, 66),
                'lon': (65, 101),
                'step': 1
            },
            {
                'lat': (930, 966),
                'lon': (1115, 1151),
                'step': 1
            }
        ]
    },
    'wv': {
        'r1': [
            {
                'lat': (0, 36),
                'lon': (55, 91),
                'step': 1
            },
            {
                'lat': (900, 936),
                'lon': (1105, 1141),
                'step': 1
            }
        ],
        'r2': [
            {
                'lat': (30, 66),
                'lon': (65, 101),
                'step': 1
            },
            {
                'lat': (900, 936),
                'lon': (1105, 1141),
                'step': 1
            }
        ]
    },
    'sst': {
        'r1': [
            {
                'lat': (0, 36),
                'lon': (55, 91),
                'step': 1
            },
            {
                'lat': (900, 936),
                'lon': (1105, 1141),
                'step': 1
            }
        ],
        'r2': [
            {
                'lat': (30, 66),
                'lon': (65, 101),
                'step': 1
            },
            {
                'lat': (930, 966),
                'lon': (1115, 1151),
                'step': 1
            }
        ]
    },
    'sss': {
        'r1': [
            {
                'lat': (0, 36),
                'lon': (55, 91),
                'step': 1
            },
            {
                'lat': (900, 936),
                'lon': (1105, 1141),
                'step': 1
            }
        ],
        'r2': [
            {
                'lat': (30, 66),
                'lon': (65, 101),
                'step': 1
            },
            {
                'lat': (900, 936),
                'lon': (1105, 1141),
                'step': 1
            }
        ]
    },
}

region = {
    'v10': {
        'r1': {
            'south': 18.5,
            'north': 22,
            'west': 116.5,
            'east': 120,
            'step': 0.25
            },
        'r2': {
            'south': 19.5,
            'north': 23,
            'west': 121.5,
            'east': 125,
            'step': 0.25
        }
    },
    'u10': {
        'r1': {
            'south': 18.5,
            'north': 22,
            'west': 116.5,
            'east': 120,
            'step': 0.25
        },
        'r2': {
            'south': 19.5,
            'north': 23,
            'west': 121.5,
            'east': 125,
            'step': 0.25
        }
    },
    'swh': {
        'r1': {
            'south': 18.5,
            'north': 22,
            'west': 116.5,
            'east': 120,
            'step': 0.5
        },
        'r2': {
            'south': 19.5,
            'north': 23,
            'west': 121.5,
            'east': 125,
            'step': 0.5
        }
    },
    'wu': {
        'r1': {
            'south': 15,
            'north': 18.5,
            'west': 110.5,
            'east': 114,
            'step': 0.1
        },
        'r2': {
            'south': 18,
            'north': 21.5,
            'west': 111.5,
            'east': 115,
            'step': 0.1
        }
    },
    'wv': {
        'r1': {
            'south': 15,
            'north': 18.5,
            'west': 110.5,
            'east': 114,
            'step': 0.1
        },
        'r2': {
            'south': 18,
            'north': 21.5,
            'west': 111.5,
            'east': 115,
            'step': 0.1
        }
    },
    'sst': {
        'r1': {
            'south': 15,
            'north': 18.5,
            'west': 110.5,
            'east': 114,
            'step': 0.1
        },
        'r2': {
            'south': 18,
            'north': 21.5,
            'west': 111.5,
            'east': 115,
            'step': 0.1
        }
    },
    'sss': {
        'r1': {
            'south': 15,
            'north': 18.5,
            'west': 110.5,
            'east': 114,
            'step': 0.1
        },
        'r2': {
            'south': 18,
            'north': 21.5,
            'west': 111.5,
            'east': 115,
            'step': 0.1
        }
    }
}

# 归一化的最大最小未知
max_min = {
    'r1': {
        'u10': {
            'max': 26.80657958984375,
            'min': -31.98837208273438
        },
        'v10': {
            'max': 29.104354858398438,
            'min': -28.124863731723412
        },
        'swh': {
            'max': 0.0,
            'min': 13.766881942749023
        },
        'wu': {
            'max': 1.0,
            'min': -1.0
        },
        'wv': {
            'max': 3.0,
            'min': -4.0
        },
        'sst': {
            'max': 31.34875,
            'min': 20.29375
        },
        'sss': {
            'max': 35.136,
            'min': 31.992
        }
    },
    'r2': {
        'u10': {
            'max': 27.908113217056584,
            'min': -29.056054158065447
        },
        'v10': {
            'max': 31.02163502751372,
            'min': -27.03924412878921
        },
        'swh': {
            'max': 0.0,
            'min': 11.986807117124465
        },
        'wu': {
            'max': 1.0,
            'min': 0.0
        },
        'wv': {
            'max': 1.0,
            'min': -1.0
        },
        'sst': {
            'max': 31.30125,
            'min': 15.4375
        },
        'sss': {
            'max': 35.315,
            'min': 32.28
        },
    },
}

# sst和sss未知
variables = {
    'v10': '10 metre V wind component',
    'u10': '10 metre U wind component',
    'swh': 'H03',
    'wu': 'CUR',
    'wv': 'CVR',
    'sst': 'TEM',
    'sss': 'SAL'
}

# current待添加
var_folder = {
    'win': {
        'windGrb': {
            'u10': 'windU',
            'v10': 'windV'
        },
        'windUc': {
            'u10': 'UT',
            'v10': 'VT'
        }
    },
    'cur': {
        'Current': {
            'wu': 'CUR',
            'wv': 'CVR'
        }
    }
}


mixture_vars = {
    'cur': ['wu', 'wv'],
    'win': ['u10', 'v10']
}
