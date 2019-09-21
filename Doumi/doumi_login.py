# -*- coding: utf-8 -*-
# @Time    : 2019/7/14 9:29
# @Author  : Esbiya
# @Email   : 18829040039@163.com
# @File    : demo.py
# @Software: PyCharm


import requests
import execjs
import re
import getpass
from utils import *
from cookies_pool import RedisClient


class DoumiLogin:

    def __init__(self, username: str = None, password: str = None):
        self.site = 'doumi'
        self.logger = get_logger()
        self.username = username
        self.password = password
        self.redis_client = RedisClient(self.logger)
        self.session = requests.session()
        self.session.headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.80 Safari/537.36'
        }
        # 密码错误重置初始化
        self.reset_flag = False

    def check_islogin(self, cookies):
        """
        检查登录状态, 访问登录页面出现跳转至主页则登录成功
        :return:
        """
        res = self.session.get('https://vip.doumi.com/login', cookies=cookies)
        if res.url == 'https://vip.doumi.com/vipcloud/enterprise/information/material':
            self.logger.info('登录成功! ')
            self.redis_client.save_cookies(self.site, self.username, cookies)
            return True
        return False

    def _get_csrf_token(self):
        """
        从登录页面获取 csrf_token 认证参数
        :return: str
        """
        res = self.session.get('https://vip.doumi.com/login')
        csrf_token = re.search(r"""\("X-CSRF-TOKEN", '(.*?)'\)""", res.text, re.S).group(1)
        return csrf_token

    def _encrypt_password(self):
        """
        RSA加密
        :return: 密码加密字符串
        """
        with open('encrypt.js', 'rb') as f:
            js = f.read().decode()

        ctx = execjs.compile(js)
        encrypt_pwd = ctx.call('encrypt', self.password)
        return encrypt_pwd

    @loopUnlessSeccessOrMaxTry(3, sleep_time=3)
    def login(self):
        """
        模拟登录
        :return:
        """
        login_api = 'https://vip.doumi.com/employer/user/ajaxlogin'
        csrf_token = self._get_csrf_token()
        data = {
            'phone_login': self.username,
            'passwd_login': self._encrypt_password(),
            '_token': csrf_token,
            'redirect_url': ''
        }

        self.session.headers.update({
            'x-csrf-token': csrf_token,
            'x-requested-with': 'XMLHttpRequest'
        })

        res = self.session.post(login_api, data=data)
        cookies = res.cookies.get_dict()
        if self.check_islogin(cookies):
            return cookies
        elif res.json()['msg'] == '账户或密码有误':
            self.reset_flag = True
            raise Exception('账号或密码错误! ')
        raise Exception('登录失败: ', res.json()['msg'])

    @check_user()
    def run(self, load_cookies: bool = True):

        if load_cookies:
            cookies = self.redis_client.load_cookies(self.site, self.username)
            if cookies:
                if self.check_islogin(cookies):
                    return cookies
                self.logger.warning('cookies已过期')

        return self.login()


if __name__ == '__main__':
    x = DoumiLogin().run()
    print(x)

