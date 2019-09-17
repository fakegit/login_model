# -*- coding: utf-8 -*-
# @Time    : 2019/8/6 20:08
# @Author  : Esbiya
# @Email   : 18829040039@163.com
# @File    : steam_login.py
# @Software: PyCharm


import requests
import execjs
from bs4 import BeautifulSoup
from utils import *
from chaojiying import image_to_text
from cookies_pool import RedisClient


class SteamLogin:

    def __init__(self, username: str = None, password: str = None):
        self.site = 'steam'
        self.logger = get_logger()
        self.username = username
        self.password = password
        self.redis_client = RedisClient(self.logger)
        self.session = requests.session()
        self.session.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.80 Safari/537.36'
        }

        # 密码错误重置初始化
        self.reset_flag = False

    def check_islogin(self, cookies):
        """
        检查是否登录成功
        :return:
        """
        res = self.session.get('https://store.steampowered.com/', cookies=cookies)
        if 'account_pulldown' in res.text:
            bsobj = BeautifulSoup(res.text, 'lxml')
            nickname = bsobj.select('#account_pulldown')[0].get_text()
            self.logger.info('Cookies 有效! ')
            self.logger.info(f'Hello, {nickname}! ')
            return True
        return False

    def _init_cookies(self):
        self.session.get('https://store.steampowered.com/')

    def _get_rsakey(self):
        """
        获取 RSA 加密参数
        :return:
        """
        url = 'https://store.steampowered.com/login/getrsakey/'
        data = {
            'donotcache': int(time.time() * 1000),
            'username': self.username
        }
        res = self.session.post(url, data=data).json()
        rsa_mod = res['publickey_mod']
        rsa_exp = res['publickey_exp']
        rsa_timestamp = res['timestamp']
        return rsa_mod, rsa_exp, rsa_timestamp

    def _encrypt_pwd(self, rsa_mod, rsa_exp):
        with open('encryptPwd.js', 'rb') as f:
            js = f.read().decode()

        ctx = execjs.compile(js)
        return ctx.call('encrypt', self.password, rsa_mod, rsa_exp)

    @loopUnlessSeccessOrMaxTry(3, sleep_time=3)
    def login(self):
        login_api = 'https://store.steampowered.com/login/dologin/'

        self._init_cookies()
        rsa_mod, rsa_exp, rsa_timestamp = self._get_rsakey()
        pwd = self._encrypt_pwd(rsa_mod, rsa_exp)

        data ={
            'donotcache': int(time.time() * 1000),
            'password': pwd,
            'username': self.username,
            'twofactorcode': '',
            'emailauth': '',
            'loginfriendlyname': '',
            'captchagid': '-1',
            'captcha_text': '',
            'emailsteamid': '',
            'rsatimestamp': rsa_timestamp,
            'remember_login': 'false'
        }

        res = self.session.post(login_api, data=data).json()
        if res['success']:
            transfer_urls = res['transfer_urls']
            transfer_parameters = res['transfer_parameters']
            resp = self.session.post(transfer_urls[1], data=transfer_parameters)
            if 'transfer_success' in resp.text:
                self.logger.info('登录成功! ')
                cookies = self.session.cookies.get_dict()
                self.redis_client.save_cookies(self.site, self.username, cookies)
                return True
            raise Exception('登录失败! ')
        else:
            if res['captcha_needed']:
                self.logger.info('此次登录需要验证码! ')
                return False
            elif res['message'] == '您输入的帐户名称或密码错误。' or \
                    res['message'] == 'The account name or password that you have entered is incorrect.':
                self.reset_flag = True
                raise Exception('账号或密码错误! ')

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
    SteamLogin().run(load_cookies=True)
