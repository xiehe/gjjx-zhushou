#!/usr/bin/env python
# coding: utf-8

import random
import re
from PIL import Image
from io import BytesIO

header = {
    'User-Agent' : 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.13 Safari/537.36',
    'Referer': 'http://www.gjjx.com.cn'
}

class Login:
    def __init__(self, session):
        self.session = session
        self.captcha_path = 'temp/captcha.png'

    # 获取验证码
    def getCaptcha(self):
        """
        @return Bool, 文件流
        """
        url = 'http://www.gjjx.com.cn/member/captcha/' + str(random.random())
        r = self.session.get(url)
        if r.status_code == 200:
            im = Image.open(BytesIO(r.content))
            im.save(self.captcha_path, 'png')
            return True, r.content
        else:
            return False, r.content

    # 登录
    def login(self, payload):
        url = 'http://www.gjjx.com.cn/member/login?hash=' + str(random.random())
        r = self.session.post(url, data=payload, headers=header)
        json = r.json()

        user = {
            'name': '', # 真实姓名
        }
        if json['code'] == 10008:
            user['name'] = json['data']['user']['truename']
            return True, user
        else:
            return False, self.login_err_msg(json['code'])

    # 登录错误提示
    def login_err_msg(self, code):
        d = {
            20000: u'提交参数错误',
            20002: u'用户未激活或被锁定',
            20003: u'用户名或密码错误',
            20004: u'验证码错误',
            20005: u'用户不存在',
            20001: u'用户已登陆',
        }
        if code == 20004 or code == 20003:
            self.getCaptcha()
        return d[code]