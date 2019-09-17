# -*- coding: utf-8 -*-
# @Time    : 2019/7/14 13:52
# @Author  : Esbiya
# @Email   : 18829040039@163.com
# @File    : login.py
# @Software: PyCharm

from utils import *
import chardet
from cookies_pool import RedisClient
import requests
import execjs
from bs4 import BeautifulSoup


class LrtsLogin:

    def __init__(self, username: str = None, password: str = None):
        self.site = 'lrts'
        self.logger = get_logger()
        self.username = username
        self.password = password
        self.redis_client = RedisClient(self.logger)
        self.session = requests.session()
        self.session.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.80 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest'
        }
        # 密码错误重置
        self.reset_flag = False

    def check_islogin(self, cookies):
        res = self.session.get('http://www.lrts.me/index', cookies=cookies)
        html = res.content.decode(chardet.detect(res.content)['encoding'])
        bsobj = BeautifulSoup(html, 'lxml')
        if bsobj.select('h4.nowrap a'):
            nickname = bsobj.select('h4.nowrap a')[0].get_text()
            self.logger.info('登录成功！')
            self.logger.info('Hello, {}!'.format(nickname))
            self.redis_client.save_cookies(self.site, self.username, cookies)
            return True
        return False

    def _get_token(self):
        url = 'http://www.lrts.me/user/login_token.do'

        data = {
            'accountName': self.username
        }

        res = self.session.post(url, data=data).json()
        return res['data']

    def _encrypt_pwd(self, token):
        with open('encrypt.js', 'rb') as f:
            js = f.read().decode()

        ctx = execjs.compile(js)
        return ctx.call('encrypt_pwd', self.password, token)

    @loopUnlessSeccessOrMaxTry(3, sleep_time=3)
    def login(self):
        api = 'http://www.lrts.me/user/login.do'

        token = self._get_token()
        pwd = self._encrypt_pwd(token)
        data = {
            'accountName': self.username,
            'hashPass': pwd,
            'autoLogin': '1',
            'validateCode': ''
        }
        res = self.session.post(api, data=data)
        cookies = res.cookies.get_dict()
        if self.check_islogin(cookies):
            self.logger.info('Cookies 有效期: {} 天'.format(int(res.json()['data']['expires'] / 86400)))
            return True
        elif res.json()['errMsg'] == '帐号或密码错误':
            self.reset_flag = True
            raise Exception('账号或密码错误! ')
        raise Exception('登录失败: ', res.json()['errMsg'])

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
    LrtsLogin().run()
