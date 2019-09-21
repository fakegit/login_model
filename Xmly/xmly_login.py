# -*- coding: utf-8 -*-
# @Time    : 2019/7/25 23:23
# @Author  : Esbiya
# @Email   : 18829040039@163.com
# @File    : xmly_login.py
# @Software: PyCharm


import requests
import execjs
from utils import *
from cookies_pool import RedisClient


class XmlyFMLogin:

    def __init__(self, username: str = None, password: str = None):
        self.site = 'xmly'
        self.logger = get_logger()
        self.username = username
        self.password = password
        self.redis_client = RedisClient(self.logger)
        self.session = requests.session()
        self.session.headers = {
            'Host': 'www.ximalaya.com',
            'Referer': 'https://www.ximalaya.com/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.80 Safari/537.36'
        }

        # 密码错误重置初始化
        self.reset_flag = False

        with open('signature.js', 'rb') as f:
            js = f.read().decode()

        self.ctx = execjs.compile(js)

    @loopUnlessSeccessOrMaxTry(3, sleep_time=3)
    def check_islogin(self, cookies):
        res = self.session.get('https://www.ximalaya.com/revision/main/getCurrentUser', cookies=cookies).json()
        if res['ret'] == 200:
            nickname = res['data']['nickname']
            self.logger.info('登录成功！')
            self.logger.info('Hello, {}! '.format(nickname))
            self.redis_client.save_cookies(self.site, self.username, cookies)
            return True
        return False

    def _get_token(self):
        url = 'https://www.ximalaya.com/passport/token/login'
        res = self.session.get(url).json()
        if res['ret'] == 0:
            return res['token']
        return False

    def _get_signature(self, params):
        return self.ctx.call('get_signature', params)

    def _encrypt_pwd(self, token):
        return self.ctx.call('encrypwd', self.password, token)

    def _verify_account(self, token):
        """
        验证账号是否存在
        :return:
        """
        api = 'https://www.ximalaya.com/passport/login/checkAccount'

        data = {
            'email': self.username,
            'nonce': token,
        }

        params = ''
        for key, value in data.items():
            params += key + '=' + value + '&'
        params += "e1996c7d6e0ff0664b28af93a2eeff8f8cae84b2402d158f7bb115b735a1663d"
        signature = self._get_signature(params)

        data.update({
            'signature': signature
        })

        res = self.session.post(api, data=data).json()
        if res['success']:
            return True
        return False

    @loopUnlessSeccessOrMaxTry(3, sleep_time=3)
    def login(self):
        """
        模拟登录
        :return:
        """
        api = 'https://www.ximalaya.com/passport/v4/security/popupLogin'
        token = self._get_token()

        if token:
            if not self._verify_account(token):
                self.logger.error('账号不存在! ')
                return False

        # token 是一次性的
        token = self._get_token()
        if token:
            encrypt_pwd = self._encrypt_pwd(token)

            data = {
                'password': encrypt_pwd,
                'rememberMe': 'true',
                'account': self.username
            }

            res = self.session.post(api, data=data)
            cookies = res.cookies.get_dict()
            if self.check_islogin(cookies):
                return cookies
            if res.json()['errorMsg'] == '账号或密码不正确！':
                self.reset_flag = True
                raise Exception('账号或密码错误! ')
            raise Exception('登录失败: {} '.format(res.json()['errorMsg']))

    @check_user()
    def run(self, load_cookies=True):

        if load_cookies:
            cookies = self.redis_client.load_cookies(self.site, self.username)
            if cookies:
                if self.check_islogin(cookies):
                    return cookies
                self.logger.warning('Cookies 已过期')

        return self.login()


if __name__ == '__main__':
    x = XmlyFMLogin().run(load_cookies=False)
    print(x)
