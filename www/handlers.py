#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = 'XFanYu'
__email__ = 'Xfanyu@outlook.com'
'''
url handlers.
'''
import calendar
import time

from code import mail
from coroweb import gp
from models import User, Resource, get_eam, admin_ids


# 辅助函数,用来识别eamOrId是eam号还是身份证号
def where(eamOrId):
    if len(eamOrId) > 14:
        return 'id=?'
    return 'eam=?'


# 判断是否更新用户user的隔离信息
def update_qrt(user):
    if user.qrt == '是':
        # 日期(年-月-日 时:分:秒) -> 时间戳
        date_format = '%Y-%m-%d %H:%M:%S'
        time_array = time.strptime(user.qrt_time, date_format)
        time_stamp = int(time.mktime(time_array))
        gap = calendar.timegm(time.gmtime()) - time_stamp
        days = gap // 86400
        if days > 0:
            user.qrt_days_remain = user.qrt_days_remain - days
            if user.qrt_days_remain <= 0:
                user.qrt = '否'
                user.qrt_days_all = 0
                user.qrt_days_remain = 0
                user.qrt_time = '暂未设置'
            return True
    return False


# get request handler functions
@gp('/', 'GET')
def get_home():
    return {'__template__': 'home.html'}


@gp('/register', 'GET')
def get_register():
    return {'__template__': 'register.html'}


@gp('/login', 'GET')
def get_login():
    return {'__template__': 'login.html'}


@gp('/forget', 'GET')
def get_forget():
    return {'__template__': 'forget.html'}


@gp('/user/{eamOrId}', 'GET')
async def get_user(eamOrId):
    users = await User.find_all(where(eamOrId), [eamOrId])
    user = users[0]
    if update_qrt(user):
        await user.update()
    return {
        'user': user,
        '__template__': 'user.html'
    }


@gp('/resource/{eamOrId}', 'GET')
async def get_resource(eamOrId):
    users = await User.find_all(where(eamOrId), [eamOrId])
    user = users[0]
    resources_all = await Resource.find_all('area=?', [user.area])
    resource_apply, resource_ratify = user.resource_apply, user.resource_ratify
    resources_apply, resources_ratify = [], []
    if resource_apply != '':
        resource_apply = resource_apply.split(',')
        for ele in resource_apply:
            name, count = ele.split(':')
            resources_apply.append({"name": name, "count": count})
    if resource_ratify != '':
        resource_ratify = resource_ratify.split(',')
        for ele in resource_ratify:
            name, count = ele.split(':')
            resources_ratify.append({"name": name, "count": count})
    return {
        'resources_all': resources_all,
        'resources_apply': resources_apply,
        'resources_ratify': resources_ratify,
        '__template__': 'resource.html'
    }


@gp('/manage/{eamOrId}', 'GET')
async def get_manage(eamOrId):
    users = await User.find_all(where(eamOrId), [eamOrId])
    users = await User.find_all('area=?', [users[0].area])
    mix_infos = []
    for user in users:
        # 更新隔离信息
        if update_qrt(user):
            await user.update()
        resource_apply = user.resource_apply
        if resource_apply != '':
            resource_apply = resource_apply.split(',')
            for ele in resource_apply:
                name, count = ele.split(':')
                info = {
                    "username": user.username,
                    "eam": user.eam,
                    "name": name,
                    "count": count
                }
                mix_infos.append(info)
    return {
        'users': users,
        'mixInfos': mix_infos,
        '__template__': 'manage.html'
    }


# post request handler functions
@gp('/register', 'POST')
async def post_register(*, email, ID, username=None, password=None, area=None, admin_id=None):
    users = await User.find_all('id=?', [ID])
    if len(users) > 0:
        # 身份证已注册
        print('registered ID')
        return 0
    # 发送邮箱验证码(用于注册账号)
    if username is None:
        code, success = mail(email, register=True, ID=ID)
        if success:
            print('send validCode: %s(for register) successful!!!!!!!!' % code)
        else:
            print('fail to send validCode(for register)!!')
        return code
    else:
        if admin_id != '111111':
            exist = False
            for admin_id_r in admin_ids:
                if admin_id_r == admin_id:
                    exist = True
                    break
            if not exist:
                print('invalid admin ID: %s' % admin_id)
                # 无效的管理员ID
                return 1
            users = await User.find_all('admin_id=?', [admin_id])
            if len(users) > 0:
                print('registered admin ID')
                # 管理员ID已注册
                return 2
        user = User(ID=ID, eam=str(get_eam()), username=username,
                    password=password, area=area, email=email, admin_id=admin_id)
        await user.save()
        # 注册成功
        print('register successful!!!!!!!!')
        return 3


@gp('/login', 'POST')
async def post_login(*, eamOrId, password):
    admin = 0
    users = await User.find_all(where(eamOrId), [eamOrId])
    # eam号/身份证号不存在
    if len(users) == 0:
        print('unknown eam or ID')
        return [0, admin]
    user = users[0]
    if user.password != password:
        print('eam号/身份证号错误或密码错误')
        return [1, admin]
    if user.admin_id != '111111':
        admin = 1
    print('login successful!!!!!!!!')
    return [2, admin]


@gp('/forget', 'POST')
async def post_forget(*, email, eamOrId, password=None):
    # 查找数据库
    if len(eamOrId) < 15:
        eam, ID = eamOrId, None
        users = await User.find_all('eam=?', [eamOrId])
    else:
        eam, ID = None, eamOrId
        users = await User.find_all('id=?', [eamOrId])
    # eam号/身份证号不存在
    if len(users) == 0:
        print('unknown eam or ID')
        return 0
    # 发送邮箱验证码(用于修改密码)
    if password is None:
        code, success = mail(email, register=False, eam=eam, ID=ID)
        if success:
            print('send validCode: %s(for reset password) successful!!!!!!!!' % code)
        else:
            print('fail to send validCode(for reset password)!!')
        return code
    else:
        user = users[0]
        user.password = password
        await user.update()
        # 修改密码成功
        print('reset password successful!!!!!!!!')
        return 1


@gp('/user/{eamOrId}', 'POST')
async def post_user(*, eamOrId, username=None, area=None, email=None, new_pwd=None):
    users = await User.find_all(where(eamOrId), [eamOrId])
    user = users[0]
    if username:
        user.username = username
    if area:
        user.area = area
    if email:
        user.email = email
    if new_pwd:
        user.password = new_pwd
    await user.update()
    # 修改用户个人信息成功
    print('reset user information successful!!!!!!!!')
    return 1


@gp('/resource/{eamOrId}', 'POST')
async def post_resource(*, eamOrId, name, count, price=None, description=None):
    users = await User.find_all(where(eamOrId), [eamOrId])
    user = users[0]
    resources = await Resource.find_all('name=?', [name])
    # 用户请求防护用具
    if price is None:
        resource_apply = user.resource_apply
        if resource_apply == '':
            user.resource_apply = '%s:%s' % (name, count)
        else:
            resource_apply = resource_apply.split(',')
            for ele in resource_apply:
                if name == ele.split(':')[0]:
                    print('you had applied resource: %s!! please wait patiently!' % name)
                    return 0
            user.resource_apply += ',%s:%s' % (name, count)
        await user.update()
        print('apply resource: %s successful!!' % name)
        return 1
    # 管理员上传防护用具
    area = user.area
    if len(resources) > 0:
        for resource in resources:
            if resource.area == area:
                resource.count += int(count)
                await resource.update()
                print('add resource: %s successful!!!!!!!!' % name)
                return 0
    resource = Resource(name=name, area=area, count=int(count),
                        price=float(price), description=description)
    await resource.save()
    # 上传防护用具成功
    print('upload resource: %s successful!!!!!!!!' % name)
    return 1


@gp('/manage/{eamOrId}', 'POST')
async def post_manage(*, eamOrId, eamOrIdU, name=None, qrt_days_all=None, email=None, password=None):
    users = await User.find_all(where(eamOrIdU), [eamOrIdU])
    user = users[0]
    # 批准防护用具
    if name:
        area = user.area
        resources = await Resource.find_all('name=?', [name])
        for resource in resources:
            if area == resource.area:
                count = resource.count
                resource_apply = user.resource_apply.split(',')
                print(count, resource_apply)
                for ele in resource_apply:
                    name_r, nums = ele.split(':')
                    if name == name_r:
                        nums = int(nums)
                        if count < nums:
                            print('fail to ratify! resource: %s is not enough!' % name)
                            return 0
                        if user.resource_ratify == '':
                            user.resource_ratify = ele
                        else:
                            user.resource_ratify += ',%s' % ele
                        resource_apply.remove(ele)
                        user.resource_apply = ','.join(resource_apply)
                        await user.update()
                        resource.count -= nums
                        await resource.update()
                        print('ratify resource: %s successful!!!!!!!!' % name)
                        return 1
    # 设置用户信息
    if qrt_days_all:
        # 取消用户的隔离状态
        if qrt_days_all == '0':
            user.qrt = '否'
            user.qrt_days_all = 0
            user.qrt_days_remain = 0
            user.qrt_time = '暂未设置'
            print('success to cancel the qrt state of user: %s!!!!!!!!' % user.username)
            await user.update()
            return 0
        user.qrt = '是'
        user.qrt_days_all = int(qrt_days_all)
        user.qrt_days_remain = int(qrt_days_all)
        # 时间戳 -> 日期(年-月-日 时:分:秒)
        date_format = '%Y-%m-%d %H:%M:%S'
        time_array = time.localtime(calendar.timegm(time.gmtime()))
        user.qrt_time = time.strftime(date_format, time_array)
    if email:
        user.email = email
    if password:
        user.password = password
    await user.update()
    print('manage user information successful!!!!!!!!')
    return 0
