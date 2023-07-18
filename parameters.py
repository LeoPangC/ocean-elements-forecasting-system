models_path = {
    'u10_r1': 'u10/single_ConvLSTM_u__single_ConvLSTM_s_e98.h5',
    'v10_r1': 'v10/single_ConvLSTM_u__single_ConvLSTM_s_e101.h5',
    'swh_r1': 'swh/single_ConvLSTM_u__single_ConvLSTM_s_e17.h5',
    'wu_r1': 'w_u/w_u_r1_U_current.h5',
    'wv_r1': 'w_v/w_v_r1_V_current.h5',
    'sst_r1': 'sst/single_ConvLSTM_u__single_ConvLSTM_s_e61.h5',
    'sss_r1': 'sss/single_ConvLSTM_u__single_ConvLSTM_s_e200.h5',
    'bc_u10': 'bc_u10/3CNN_244_u10.h5',
    'bc_v10': 'bc_v10/3CNN_260_v10.h5',
    '3DS': '3D_Salinity',
    '3DT': '3D_Temperature'
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
                'lat': (136, 205),
                'lon': (300, 353),
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
                'lat': (0, 102),
                'lon': (0, 102),
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
            'south': 4,
            'north': 21,
            'west': 105,
            'east': 118,
            'step': 0.25
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
            'north': 25,
            'west': 105,
            'east': 115,
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
            'max': 23.395458,
            'min': -25.674194
        },
        'v10': {
            'max': 24.201258,
            'min': -24.86848
        },
        'swh': {
            'max': 10.16,
            'min': 0.01
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
            'max': 38.20107421875002,
            'min': 11.959863281250023
        },
        'sss': {
            'max': 35.060073223896325,
            'min': 24.42887927562697
        },
        'bc_u10': {
            'max': 21.595853753065384,
            'min': -24.532222501514845
        },
        'bc_v10': {
            'max': 27.40936279296875,
            'min': -24.59051513671875
        }
    }
}

# 3D归一化
max_min_3D = {
    '3DT': {
        0: {
            'max': 318.66748,
            'min': 268.41586
            },
        1: {
            'max': 317.00668,
            'min': 267.2094
        },
        2: {
            'max': 315.33795,
            'min': 265.6961
        },
        3: {
            'max': 313.6513,
            'min': 264.16827
        },
        4: {
            'max': 311.90735,
            'min': 263.02158
        }
    },
    '3DS': {
        0: {
            'max': 35.060073223896325,
            'min': 24.42887927562697
        }
    }
}

# sst和sss未知
variables = {
    'v10': '10 metre V wind component',
    'u10': '10 metre U wind component',
    'swh': 'H03',
    'wu': 'CUR',
    'wv': 'CVR',
    'sst': 'Temperature',
    'sss': 'SAL'
}

# current待添加
var_folder = {
    'win': {
        'windGrb': {
            'u10': 'windU',
            'v10': 'windV'
        },
        '': {
            'u10': 'UT',
            'v10': 'VT'
        }
    },
    'cur': {
        'Current': {
            'wu': 'CUR',
            'wv': 'CVR'
        }
    },
    'swh': {
        'H03': {
            'swh': ''
        }
    },
    'sst': {
        'TT': {
            'sst': ''
        }
    },
    '3DT': {
        'TT': {
            '3DT': ''
        }
    },
    '3DS': {
        'SAL': {
            '3DS': ''
        }
    },
}


mixture_vars = {
    'cur': ['wu', 'wv'],
    'win': ['u10', 'v10'],
    'swh': ['swh'],
    'sst': ['sst'],
    '3DT': ['3DT'],
    '3DS': ['3DS']
}

# 元素数据存储文件
ele_dir = {
    'sst': {
        'Uc': 'TT'
    },
    'sss': {
        'Uc': 'SAL'
    },
    'swh': {
        'Uc': 'H03'
    },
    'win': {
        'Uc': '',
        'Grb': 'windGrb'
    },
    'cur': {
        'Uc': 'Current'
    },
    '3DS': {
        'Uc': 'SAL'
    },
    '3DT': {
        'Uc': 'TT'
    }
}

ele_floder = {
    'sst': 'TT',
    'sss': 'SAL',
    'swh': 'H03',
    'win': 'wind',
    'cur': 'Uc',
}