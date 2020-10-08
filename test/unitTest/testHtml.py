#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = 'XFanYu'
__email__ = 'Xfanyu@outlook.com'
'''
Html Test.
'''
import time
import unittest
from selenium import webdriver


# 测试前端的登录界面和注册界面
class TestHtml(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Chrome()
        self.base_url = "http://127.0.0.1:9000/"
        print('Start Html Testing!')

    def tearDown(self):
        self.driver.close()
        print('Finish Html Testing!')

    # 测试注册界面
    def test_register(self):
        browser = self.driver
        browser.get(self.base_url + 'register')

        user = {
            'username': 'admin3',
            'ID': '13579246803333333X',
            'admin_id': '$$%*-35213-qxUqED',
            'area': '天津市-天津市-津南区',
            'email': '123@outlook.com',
            'pwd': '123456@tj',
            'pwd1': '123456@tj',
            'code': '12345'
        }
        # 测试用户名
        cases1 = [['', user['ID'], user['admin_id'], user['area'], user['email'],
                   user['pwd'], user['pwd1'], user['code'], '请输入用户名！'],
                  ['1user', user['ID'], user['admin_id'], user['area'], user['email'],
                   user['pwd'], user['pwd1'], user['code'], '用户名以字母开头，由数字字母组成！'],
                  ['user1!', user['ID'], user['admin_id'], user['area'], user['email'],
                   user['pwd'], user['pwd1'], user['code'], '用户名以字母开头，由数字字母组成！']]
        # 测试身份证号码
        cases2 = [[user['username'], '', user['admin_id'], user['area'], user['email'],
                   user['pwd'], user['pwd1'], user['code'], '请输入身份证号码！'],
                  [user['username'], '1234567890123456', user['admin_id'], user['area'], user['email'],
                   user['pwd'], user['pwd1'], user['code'], '请输入正确的身份证号码！']]
        # 测试地区
        cases3 = [[user['username'], user['ID'], user['admin_id'], '', user['email'],
                   user['pwd'], user['pwd1'], user['code'], '地区不能为空！']]
        # 测试邮箱
        cases4 = [[user['username'], user['ID'], user['admin_id'], user['area'], '',
                   user['pwd'], user['pwd1'], user['code'], '邮箱不能为空！'],
                  [user['username'], user['ID'], user['admin_id'], user['area'], '123qq.com',
                   user['pwd'], user['pwd1'], user['code'], '邮箱格式不正确！'],
                  [user['username'], user['ID'], user['admin_id'], user['area'], '123@qqcom',
                   user['pwd'], user['pwd1'], user['code'], '邮箱格式不正确！']]
        # 测试密码
        cases5 = [[user['username'], user['ID'], user['admin_id'], user['area'], user['email'],
                   '12345@tj', user['pwd1'], user['code'], '密码应至少包括9个字符！'],
                  [user['username'], user['ID'], user['admin_id'], user['area'], user['email'],
                   '12345678901234tj', user['pwd1'], user['code'], '密码应包括数字、字母和特殊字符(@和#等)！']]
        cases6 = [[user['username'], user['ID'], user['admin_id'], user['area'], user['email'],
                   user['pwd'], '', user['code'], '两次输入的密码不一致！'],
                  [user['username'], user['ID'], user['admin_id'], user['area'], user['email'],
                   user['pwd'], '123456#tj', user['code'], '两次输入的密码不一致！']]

        # 注册信息初步检查通过但注册失败
        cases7 = [[user['username'], '123456789066666', user['admin_id'], user['area'], user['email'],
                   user['pwd'], user['pwd1'], user['code'], '身份证已注册！'],
                  [user['username'], user['ID'], '111', user['area'], user['email'],
                   user['pwd'], user['pwd1'], user['code'], '无效的管理员ID！'],
                  [user['username'], user['ID'], '#*&&-08784-kownkA', user['area'], user['email'],
                   user['pwd'], user['pwd1'], user['code'], '管理员ID已注册！']]

        register_info = [[cases1, 'username_err', False], [cases2, 'ID_err', False],
                         [cases3, 'area_err', False], [cases4, 'email_err', False],
                         [cases5, 'password_err', False], [cases6, 'password1_err', False],
                         [cases7[:1], 'ID_err', True], [cases7[1:], 'adminId_err', True]]

        # 注册失败测试
        for (cases, id_name, sleep) in register_info:
            for case in cases:
                # 输入用户名
                browser.find_element_by_name('username').clear()
                browser.find_element_by_name('username').send_keys(case[0])
                # 输入身份证号
                browser.find_element_by_name('ID').clear()
                browser.find_element_by_name('ID').send_keys(case[1])
                # 输入管理员ID
                browser.find_element_by_name('adminId').clear()
                browser.find_element_by_name('adminId').send_keys(case[2])
                # 输入地区
                area = browser.find_element_by_name('area')
                browser.execute_script("arguments[0].value = '%s';" % case[3], area)
                # 输入邮箱
                browser.find_element_by_name('email').clear()
                browser.find_element_by_name('email').send_keys(case[4])
                # 输入密码
                browser.find_element_by_name('password').clear()
                browser.find_element_by_name('password').send_keys(case[5])
                browser.find_element_by_name('password1').clear()
                browser.find_element_by_name('password1').send_keys(case[6])
                # 输入验证码 & 点击注册
                if sleep:
                    if id_name == 'validCode_err':
                        browser.find_element_by_id('valid').click()
                        time.sleep(3)
                    browser.find_element_by_name('validCode').clear()
                    browser.find_element_by_name('validCode').send_keys(case[7])
                    browser.find_element_by_id('registerBtn').click()
                    time.sleep(3)
                else:
                    browser.find_element_by_name('validCode').clear()
                    browser.find_element_by_name('validCode').send_keys(case[7])
                    browser.find_element_by_id('registerBtn').click()
                self.assertEqual(browser.find_element_by_id(id_name).text, case[8])

        # 注册成功测试
        cases8 = [[user['username'], user['ID'], user['admin_id'], user['area'], user['email'],
                   user['pwd'], user['pwd1'], user['code'], '注册成功！！']]
        for case in cases8:
            # 输入用户名
            browser.find_element_by_name('username').clear()
            browser.find_element_by_name('username').send_keys(case[0])
            # 输入身份证号
            browser.find_element_by_name('ID').clear()
            browser.find_element_by_name('ID').send_keys(case[1])
            # 输入管理员ID
            browser.find_element_by_name('adminId').clear()
            browser.find_element_by_name('adminId').send_keys(case[2])
            # 输入地区
            area = browser.find_element_by_name('area')
            browser.execute_script("arguments[0].value = '%s';" % case[3], area)
            # 输入邮箱
            browser.find_element_by_name('email').clear()
            browser.find_element_by_name('email').send_keys(case[4])
            # 输入密码
            browser.find_element_by_name('password').clear()
            browser.find_element_by_name('password').send_keys(case[5])
            browser.find_element_by_name('password1').clear()
            browser.find_element_by_name('password1').send_keys(case[6])
            # 输入验证码 & 点击注册
            browser.find_element_by_name('validCode').clear()
            browser.find_element_by_name('validCode').send_keys(case[7])
            browser.find_element_by_id('registerBtn').click()
            time.sleep(5)
            alert = self.driver.switch_to_alert()
            self.assertEqual(alert.text, case[8])
            alert.accept()
            browser.get(self.base_url + 'register')

        # 测试验证码
        cases9 = [[user['username'], user['ID'], user['admin_id'], user['area'], user['email'],
                   user['pwd'], user['pwd1'], '', '请输入验证码！'],
                  [user['username'], '098765432109876', user['admin_id'], user['area'], user['email'],
                   user['pwd'], user['pwd1'], user['code'], '验证码错误！']]
        register_info = [[[cases9[0]], 'validCode_err', False], [[cases9[1]], 'validCode_err', True]]
        for (cases, id_name, sleep) in register_info:
            for case in cases:
                # 输入用户名
                browser.find_element_by_name('username').clear()
                browser.find_element_by_name('username').send_keys(case[0])
                # 输入身份证号
                browser.find_element_by_name('ID').clear()
                browser.find_element_by_name('ID').send_keys(case[1])
                # 输入管理员ID
                browser.find_element_by_name('adminId').clear()
                browser.find_element_by_name('adminId').send_keys(case[2])
                # 输入地区
                area = browser.find_element_by_name('area')
                browser.execute_script("arguments[0].value = '%s';" % case[3], area)
                # 输入邮箱
                browser.find_element_by_name('email').clear()
                browser.find_element_by_name('email').send_keys(case[4])
                # 输入密码
                browser.find_element_by_name('password').clear()
                browser.find_element_by_name('password').send_keys(case[5])
                browser.find_element_by_name('password1').clear()
                browser.find_element_by_name('password1').send_keys(case[6])
                # 输入验证码 & 点击注册
                if sleep:
                    browser.find_element_by_id('valid').click()
                    time.sleep(3)
                    browser.find_element_by_name('validCode').clear()
                    browser.find_element_by_name('validCode').send_keys(case[7])
                    browser.find_element_by_id('registerBtn').click()
                    time.sleep(3)
                else:
                    browser.find_element_by_name('validCode').clear()
                    browser.find_element_by_name('validCode').send_keys(case[7])
                    browser.find_element_by_id('registerBtn').click()
                self.assertEqual(browser.find_element_by_id(id_name).text, case[8])

    # 测试登录界面
    def test_login(self):
        # 测试eam号或身份证号
        cases1 = [['', '123456@hn', '请输入eam号/身份证号！'],
                  ['1234567', '123456@hn', '请输入正确的eam号/身份证号！'],
                  ['12345678901234x', '123456@hn', '请输入正确的eam号/身份证号！'],
                  ['12345678901234567a', '123456@hn', '请输入正确的eam号/身份证号！']]
        # 测试密码
        cases2 = [['11626606', '', '请输入密码！'],
                  ['11626606', '12345678', '密码错误！'],
                  ['11626606', 'abcdefghi', '密码错误！'],
                  ['11626606', 'abcdefgh!', '密码错误！']]
        # 登录信息初步检查通过但登录失败
        cases3 = [['11626600', '123456@hn', 'eam号不存在或身份证号未注册'],
                  ['12345678901234567X', '123456@hn', 'eam号不存在或身份证号未注册']]
        cases4 = [['11626606', '123455@hn', 'eam号/身份证号错误或密码错误'],
                  ['135792468011111', '123455@hn', 'eam号/身份证号错误或密码错误']]
        # 登录成功
        cases5 = [['135792468011111', '123456@hn', '135792468011111 登录成功！！'],
                  ['11626606', '123456@hn', '11626606 登录成功！！']]
        login_info = [[cases1, 'eamOrId_err', False], [cases2, 'password_err', False],
                      [cases3, 'eamOrId_err', True], [cases4, 'password_err', True]]

        browser = self.driver
        browser.get(self.base_url + 'login')
        # 登录失败测试
        for (cases, id_name, sleep) in login_info:
            for case in cases:
                # 输入eam号/身份证号
                browser.find_element_by_name('eamOrId').clear()
                browser.find_element_by_name('eamOrId').send_keys(case[0])
                # 输入密码
                browser.find_element_by_name('password').clear()
                browser.find_element_by_name('password').send_keys(case[1])
                # 点击登录
                browser.find_element_by_id('loginBtn').click()
                if sleep:
                    time.sleep(3)
                self.assertEqual(browser.find_element_by_id(id_name).text, case[2])

        # 登录成功测试
        for case in cases5:
            # 输入eam号/身份证号
            browser.find_element_by_name('eamOrId').clear()
            browser.find_element_by_name('eamOrId').send_keys(case[0])
            # 输入密码
            browser.find_element_by_name('password').clear()
            browser.find_element_by_name('password').send_keys(case[1])
            # 点击登录
            browser.find_element_by_id('loginBtn').click()
            time.sleep(3)
            alert = self.driver.switch_to_alert()
            self.assertEqual(alert.text, case[2])
            alert.accept()
            browser.get(self.base_url + 'login')


if __name__ == "__main__":
    unittest.main()
