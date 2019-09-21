# -*- coding: utf-8 -*-
# @Time    : 2019/8/15 21:53
# @Author  : Esbiya
# @Email   : 18829040039@163.com
# @File    : kankan_login.py
# @Software: PyCharm

import requests
import execjs
import re
from urllib.parse import unquote
import getpass
from utils import *
from cookies_pool import RedisClient


class KankanLogin:

    def __init__(self, username: str = None, password: str = None):
        self.site = 'kankan'
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
        检查登录状态
        :return:
        """
        url = 'http://api.t.kankan.com/kknotify.json?'
        params = {
            'jsobj': 'G_SSUser',
            'userid': cookies['luserid'],
            'r': int(time.time() * 1000)
        }
        resp = self.session.get(url, params=params, cookies=cookies)
        result = json.loads(re.search('G_SSUser = (.*?) ;', resp.text, re.S).group(1))
        if result['status'] == 200:
            self.logger.info('Cookies 有效! ')
            nickname = result['data']['user']['nickname']
            self.logger.info('Hello, {}! '.format(nickname))
            return True
        return False

    def _encrypt_password(self, check_n, check_e, vcode):
        """
        RSA加密
        :return: 密码加密字符串
        """
        with open('encrypt.js', 'rb') as f:
            js = f.read().decode()

        ctx = execjs.compile(js)
        encrypt_pwd = ctx.call('encrypt_pwd', check_n, check_e, self.password, vcode.upper())
        return encrypt_pwd

    def _check_account(self):
        url = 'https://ilogin.kankan.com/check/?u={}&v=100'.format(self.username)
        resp = self.session.get(url)
        cookies = resp.cookies.get_dict()
        check_n = unquote(cookies['check_n'])
        check_e = cookies['check_e']
        vcode = cookies['check_result'].replace('0:', '')
        return check_n, check_e, vcode

    @loopUnlessSeccessOrMaxTry(3, sleep_time=3)
    def login(self):
        """
        模拟登录
        :return:
        """
        login_api = 'https://ilogin.kankan.com/sec2login/'

        check_n, check_e, vcode = self._check_account()
        pwd = self._encrypt_password(check_n, check_e, vcode)
        data = {
            'p': pwd,
            'u': self.username,
            'n': check_n,
            'e': check_e,
            'v': '100',
            'verifycode': vcode,
            'login_enable': '0',
            'business_type': '107'
        }

        resp = self.session.post(login_api, data=data)
        cookies = resp.cookies.get_dict()
        if cookies['blogresult'] == '0':
            self.logger.info('登录成功! ')
            nickname = cookies['usernick']
            self.logger.info('Hello, {}! '.format(nickname))
            self.redis_client.save_cookies(self.site, self.username, cookies)
            return cookies
        elif cookies['blogresult'] == '4':
            self.reset_flag = True
            raise Exception('账号或密码错误! ')
        raise Exception('登录失败: ', cookies['logindetail'])

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
    x = KankanLogin().run(load_cookies=False)
    print(x)
