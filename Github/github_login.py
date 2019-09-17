# -*- coding: utf-8 -*-
# @Time    : 2019/7/28 18:47
# @Author  : xuzhihai0723
# @Email   : 18829040039@163.com
# @File    : github_login.py
# @Software: PyCharm

import requests
from utils import *
from bs4 import BeautifulSoup
from cookies_pool import RedisClient


class GithubLogin:

    def __init__(self, username: str = None, password: str = None):
        self.site = 'github'
        self.username = username
        self.password = password
        self.logger = get_logger()
        self.redis_client = RedisClient(self.logger)
        self.session = requests.session()
        self.session.headers = {
            'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.80 Safari/537.36'
        }
        # 密码错误重置初始化
        self.reset_flag = False

    def check_islogin(self, cookies):
        res = requests.get('https://github.com/', cookies=cookies)

        if 'octolytics-actor-login' in res.text:
            self.logger.info('Cookies 有效! ')
            bsobj = BeautifulSoup(res.text, 'lxml')
            nickname = bsobj.find('meta', {'name': 'octolytics-actor-login'})['content']
            self.logger.info('Hello, {}! '.format(nickname))
            return True
        return False

    def _get_authenticity_token(self):
        """
        请求登录页获取 authenticity_token
        :return:
        """
        res = self.session.get('https://github.com/login')
        bsobj = BeautifulSoup(res.text, 'lxml')
        authenticity_token = bsobj.find('input', {'name': 'authenticity_token'})['value']
        return authenticity_token

    @loopUnlessSeccessOrMaxTry(3, sleep_time=3)
    def login(self):
        """
        模拟登录
        :return:
        """
        login_api = 'https://github.com/session'

        authenticity_token = self._get_authenticity_token()
        data = {
            'commit': 'Sign in',
            'utf8': '✓',
            'authenticity_token': authenticity_token,
            'login': self.username,
            'password': self.password,
            'webauthn-support': 'supported'
        }

        res = self.session.post(login_api, data=data, allow_redirects=False)

        if res.status_code == 302:
            self.logger.info('登录成功! ')
            self.redis_client.save_cookies(self.site, self.username, res.cookies.get_dict())
            return True
        elif 'Incorrect username or password' in res.text:
            self.reset_flag = True
            raise Exception('账号或密码错误! ')
        raise Exception('登录失败! ')

    @check_user()
    def run(self, load_cookies: bool = True):
        """
        主函数运行
        :return:
        """
        if load_cookies:
            cookies = self.redis_client.load_cookies(self.site, self.username)
            if cookies:
                if self.check_islogin(cookies):
                    return True
                self.logger.warning('Cookies 已过期! ')

        self.login()


if __name__ == '__main__':
    GithubLogin().run(load_cookies=False)
