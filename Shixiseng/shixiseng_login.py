# -*- coding: utf-8 -*-
# @Time    : 2019/7/25 15:24
# @Author  : Esbiya
# @Email   : 18829040039@163.com
# @File    : login.py
# @Software: PyCharm

import requests
import execjs
import chardet
from bs4 import BeautifulSoup
from utils import *
from cookies_pool import RedisClient


class ShixiSengLogin:

    def __init__(self, username: str = None, password: str = None):
        # 网站
        self.site = 'shixiseng'
        self.logger = get_logger()
        self.username = username
        self.password = password
        self.redis_client = RedisClient(self.logger)
        self.session = requests.session()
        self.session.headers = {
            'Referer': 'https://www.shixiseng.com/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.80 Safari/537.36'
        }
        # 密码错误重置
        self.reset_flag = False

    def check_islogin(self, cookies):
        res = self.session.get('https://www.shixiseng.com/', cookies=cookies)
        html = res.content.decode(chardet.detect(res.content)['encoding'])
        bsobj = BeautifulSoup(html, 'lxml')
        if bsobj.find('span', {'class': 'nickname'}):
            nickname = bsobj.find('span', {'class': 'nickname'}).get_text().strip()
            self.logger.info('登录成功！')
            self.logger.info('Hello, {}! '.format(nickname))
            self.redis_client.save_cookies(self.site, self.username, cookies)
            return True
        return False

    def _encrypt_pwd(self):
        with open('encrypt.js', 'r') as f:
            js = f.read()
        ctx = execjs.compile(js)
        return ctx.call('myencode', self.password)

    @loopUnlessSeccessOrMaxTry(3, sleep_time=3)
    def login(self):
        pwd = self._encrypt_pwd()
        url = 'https://www.shixiseng.com/user/login'

        data = {
            'username': self.username,
            'password': pwd,
            'remember_login': '1'
        }

        res = self.session.post(url, data=data)
        result = json.loads(res.text)
        cookies = res.cookies.get_dict()
        if self.check_islogin(cookies):
            return True
        elif result['msg'] == '密码不对' or '密码不正确':
            self.reset_flag = True
            raise Exception('账号或密码错误! ')
        raise Exception('登录失败: ', result['msg'])

    @check_user()
    def run(self, load_cookies: bool = True):

        if load_cookies:
            cookies = self.redis_client.load_cookies(self.site, self.username)
            if cookies:
                if self.check_islogin(cookies):
                    return True
                self.logger.warning('Cookies 已过期')

        self.login()


if __name__ == '__main__':
    ShixiSengLogin().run(load_cookies=False)
