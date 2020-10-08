#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = 'XFanYu'
__email__ = 'Xfanyu@outlook.com'
'''
Models for user, resource
'''
from os.path import exists, dirname
from random import choices, sample

from orm import Model, Integer, Real, Varchar

path = dirname(__file__) + '/static/data/'


# 生成一个由字符集chs组成的长为n的随机字符串,unique指示是否允许重复
def random_str(chs, n, unique=False):
    if n < 1:
        return ''
    if not unique:
        return ''.join(choices(chs, k=n))
    return ''.join(sample(chs, n))


# 获取文件中的id信息(eam号和管理员id)
def load_data():
    global eam, admin_ids
    # 获取eam号
    if exists(path + 'eam'):
        with open(path + 'eam', 'r') as rf:
            lines = rf.readlines()
            eam = int(lines[0].split(' ')[0])
    else:
        eam = 11626596
        with open(path + 'eam', 'w') as wf:
            wf.write('%s' % eam)
    # 获取管理员ID
    if exists(path + 'adminId'):
        with open(path + 'adminId', 'r') as rf:
            lines = rf.readlines()
            admin_ids = [admin_id.strip() for admin_id in lines]
    else:
        chs = 'SqcXfTVOhQiwgszFNblnLCoJKUmAWMpBGyaEduIvZxjYHkRtPeDr'
        nums = '7156420938'
        special_chs = '%@#$*&'
        admin_ids = []
        i = 0
        while i < 100:
            p1 = random_str(special_chs, 4)
            p2 = random_str(nums, 5)
            p3 = random_str(chs, 5) + random_str('ABCDE', 1)
            admin_id = '%s-%s-%s' % (p1, p2, p3)
            if admin_id not in admin_ids:
                admin_ids.append(admin_id)
                i += 1
        with open(path + 'adminId', 'w') as wf:
            buf = '%s' % admin_ids[0]
            for i in range(1, 100):
                buf += '\n%s' % admin_ids[i]
            wf.write(buf)
    return eam, admin_ids


eam, admin_ids = load_data()


# 生成eam号
def get_eam():
    global eam
    eam += 1
    with open(path + 'eam', 'w') as wf:
        wf.write('%s' % eam)
    return eam - 1


# 用户类,对应数据库中的users table
class User(Model):
    __table__ = 'users'
    # 用户基本信息
    ID = Varchar(field_type='varchar(18)', pk=True)
    eam = Varchar(field_type='varchar(12)')
    username = Varchar()
    password = Varchar(field_type='varchar(16)')
    area = Varchar()
    email = Varchar()
    # 隔离信息
    qrt = Varchar(field_type='varchar(2)', default="否")
    qrt_time = Varchar(default="暂未设置")
    qrt_days_all = Integer()
    qrt_days_remain = Integer()
    # 防护用具信息
    resource_apply = Varchar(field_type='varchar(100)', default="")
    resource_ratify = Varchar(field_type='varchar(100)', default="")
    # 管理员信息
    admin_id = Varchar(field_type='varchar(16)', default='111111')


# 防护用具类,对应数据库中的resource table
class Resource(Model):
    __table__ = 'resource'
    name = Varchar(pk=True)
    area = Varchar(pk=True)
    count = Integer()
    price = Real()
    description = Varchar(field_type='varchar(500)')
