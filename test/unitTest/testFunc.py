#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = 'XFanYu'
__email__ = 'Xfanyu@outlook.com'
'''
Function Test.
'''
import unittest

from EamSys.www.code import mail
from EamSys.www.coroweb import get_args
from EamSys.www.handlers import where, get_home, get_user, post_register, post_login


# 测试后端代码中几个重要的函数
class TestFunc(unittest.TestCase):
    def setUp(self):
        print('Start Functional Testing!')

    def tearDown(self):
        print('Finish Functional Testing!')

    # 测试发送邮箱验证码
    def test_mail(self):
        receiver = '123@outlook.com'
        eam = '11626618'
        fail_result = ('fail', False)
        fail_msg = 'fail to send validate code for register!'
        self.assertNotEqual(mail(receiver, register=True, eam=eam), fail_result, fail_msg)
        fail_msg = 'fail to send validate code for reset password!'
        self.assertNotEqual(mail(receiver, register=False, eam=eam), fail_result, fail_msg)

    # 测试函数get_args
    def test_get_args(self):
        msg = 'fail to analysis function %s!'
        rst = ((), (), False, False)
        self.assertEqual(get_args(get_home), rst, msg % 'get_home')
        rst = ((), (), False, False)
        self.assertEqual(get_args(get_user), rst, msg % 'get_user')
        rst = (('email', 'ID', 'username', 'password', 'area', 'admin_id'), ('email', 'ID'),
               True, False)
        self.assertEqual(get_args(post_register), rst, msg % 'post_register')
        rst = (('eamOrId', 'password'), ('eamOrId', 'password'), True, False)
        self.assertEqual(get_args(post_login), rst, msg % 'post_login')
        pass

    # 测试函数where
    def test_where(self):
        eidOrId1 = '11626596'
        self.assertEqual(where(eidOrId1), 'eam=?')
        eidOrId2 = '123456789012345'
        self.assertEqual(where(eidOrId2), 'id=?')


if __name__ == "__main__":
    unittest.main()
