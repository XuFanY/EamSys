#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = 'XFanYu'
__email__ = 'Xfanyu@outlook.com'
'''
Configuration
'''

# Default configurations.
default_configs = {
    'database': {
        'host': '127.0.0.1',
        'port': 3306,
        'user': 'root',
        'password': 'root',
        'db': 'EamSys'
    }
}
# Override configurations.
override_configs = {
    'database': {
        'host': '127.0.0.1'
    }
}


# 合并默认配置和override配置
def merge(default, override):
    rst = {}
    for k, v in default.items():
        if k in override:
            if isinstance(v, dict):
                rst[k] = merge(v, override[k])
            else:
                rst[k] = override[k]
        else:
            rst[k] = v
    return rst


configs = merge(default_configs, override_configs)
