#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = 'XFanYu'
__email__ = 'Xfanyu@outlook.com'
'''
send email validation code.
'''
import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr
from random import randint

pwd = 'qpdhvcuhesqedfga'  # 发件人邮箱授权码
sender = '2975380988@qq.com'  # 发件人邮箱账号


def mail(receiver, register=True, eam=None, ID=None):
    success = True
    # 生成6位随机验证码
    code = ''
    for i in range(6):
        code += str(randint(0, 9))

    # 生成邮件主题和内容
    if register:
        subject = 'EamSys注册'
        message = '您正在注册EamSys账号，您的注册验证码为：%s。请勿泄露给他人！\n' % code
    else:
        subject = '修改EamSys账号密码'
        message = '您正在修改EamSys账号的密码，您的验证码为：%s。请勿泄露给他人！\n' % code
    if ID:
        message += '注册身份证号: %s' % ID
    else:
        message += 'eam号: %s' % eam

    # 发送邮件
    try:
        msg = MIMEText(message, 'plain', 'utf-8')
        msg['From'] = formataddr(["EamSys", sender])
        msg['Subject'] = subject
        server = smtplib.SMTP_SSL("smtp.qq.com", 465)
        server.login(sender, pwd)
        server.sendmail(sender, [receiver, ], msg.as_string())
        server.quit()
    except Exception:
        success = False
        code = 'fail'
    return code, success
