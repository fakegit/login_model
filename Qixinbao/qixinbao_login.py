# -*- coding: utf-8 -*-
# @Time    : 2019/7/17 22:27
# @Author  : xuzhihai0723
# @Email   : 18829040039@163.com
# @File    : demo.py
# @Software: PyCharm

import execjs
import re
import requests
from bs4 import BeautifulSoup
from utils import *
from cookies_pool import RedisClient


class QixinbaoLogin:

    def __init__(self, username: str = None, password: str = None):
        self.site = 'qixinbao'
        self.logger = get_logger()
        self.username = username
        self.password = password
        self.redis_client = RedisClient(self.logger)
        self.session = requests.session()
        self.session.headers = {
            'Content-Type': 'application/json;charset=UTF-8',  # payload提交表单参数, 请求头中必须含有 Content-Type, 并且提交方法为 json.dumps(data)
            'Referer': 'https://www.qixin.com/auth/login?return_url=%2F',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.80 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest'
        }

        # 密码错误重置
        self.reset_flag = False

        with open('encrypt.js', 'rb') as f:
            js = f.read().decode()
        self.ctx = execjs.compile(js)
        self.codes = self.get_codes()

    @loopUnlessSeccessOrMaxTry(3, sleep_time=3)
    def check_islogin(self, cookies):
        url = 'https://www.qixin.com/user/home/center'
        res = self.session.get(url, cookies=cookies)
        if '会员中心' in res.text:
            bsobj = BeautifulSoup(res.text, 'lxml')
            nickname = bsobj.find('div', {'class': 'body'}).find('h5').get_text()
            self.logger.info('登录成功！')
            self.logger.info('Hello, {}! '.format(nickname))
            self.redis_client.save_cookies(self.site, self.username, cookies)
            return True
        return False

    def _encrypt_pwd(self):
        """
        加密密码
        :return:
        """
        return self.ctx.call('encrypt', self.password)

    @staticmethod
    def get_codes():
        """
        获取 js 加密 codes
        :return:
        """
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.80 Safari/537.36',
        }
        url = 'https://cache.qixin.com/pcweb/common.a89140e8.js'
        resp = requests.get(url, headers=headers)
        codes = {}
        for i in range(20):
            text = 'e\.default={' + str(i) + ':"(.*?)"}'
            x = re.search(text, resp.text).group(1)
            codes.setdefault(i, x)
        return codes

    def _get_header_js(self, url, data):
        """
        获取请求头中的加密参数, 加密对象为提交的表单
        :return:
        """
        return {self.ctx.call('header_key', self.codes, url): self.ctx.call('header_value', self.codes, url, data)}

    def _init_cookies(self):
        self.session.get('https://www.qixin.com/')

    @loopUnlessSeccessOrMaxTry(3, sleep_time=3)
    def login(self):
        """
        模拟登录
        :return:
        """
        self._init_cookies()
        login_api = 'https://www.qixin.com/api/user/login'
        pwd = self._encrypt_pwd()
        data = {
            'acc': self.username,
            'captcha': {
                'isTrusted': 'true'
            },
            'keepLogin': 'true',
            'pass': pwd
        }
        header_js = self._get_header_js(login_api, data)
        self.session.headers.update(header_js)
        res = self.session.post(login_api, data=json.dumps(data))
        cookies = self.session.cookies.get_dict()
        if self.check_islogin(cookies):
            return True
        elif '用户名或密码错误' in res.text:
            self.reset_flag = True
            raise Exception('账号或密码错误! ')
        raise Exception('登录失败: ', res.json()['message'])

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
    QixinbaoLogin('17570759427', 'xuzhihai0723').run(load_cookies=False)
