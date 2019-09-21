# -*- coding: utf-8 -*-
# @Time    : 2019/7/9 13:10
# @Author  : Esbiya
# @Email   : 18829040039@163.com
# @File    : openlaw.py
# @Software: PyCharm

from requests import Session
import execjs
from utils import *
from cookies_pool import RedisClient
from bs4 import BeautifulSoup


class OpenlawLogin:

    def __init__(self, username: str = None, password: str = None):
        self.site = 'openlaw'
        self.username = username
        self.password = password
        self.logger = get_logger()
        self.redis_client = RedisClient(self.logger)
        self.session = Session()
        self.session.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.80 Safari/537.36'
        }
        # 密码错误重置初始化
        self.reset_flag = False

    def check_islogin(self, cookies):
        url = 'http://openlaw.cn/user/profile.jsp'
        res = self.session.get(url, cookies=cookies)
        if 'bbp-breadcrumb-root' in res.text:
            self.logger.info('Cookies 有效! ')
            bsobj = BeautifulSoup(res.text, 'lxml')
            nickname = bsobj.select('.bbp-breadcrumb-root')[0].get_text()
            self.logger.info('Hello, {}! '.format(nickname))
            return True
        return False

    def _get_csrf(self):
        while True:
            base_url = 'http://openlaw.cn/login.jsp'
            res = self.session.get(base_url)
            cookies = res.cookies.get_dict()
            if cookies:
                soup = BeautifulSoup(res.text, 'lxml')
                _csrf = soup.find('input', {'name': '_csrf'})['value']
                return _csrf, cookies
            time.sleep(1)

    def _encrypt_pwd(self):
        with open('encryptPwd.js', 'rb') as f:
            js = f.read().decode()

        ctx = execjs.compile(js)
        encrypt_pwd = ctx.call('encrypt_pwd', self.password)
        return encrypt_pwd

    @loopUnlessSeccessOrMaxTry(3, sleep_time=3)
    def login(self):
        login_api = 'http://openlaw.cn/login'
        _csrf, cookies = self._get_csrf()
        _encrypt_pwd = self._encrypt_pwd()
        data = {
            'username': self.username,
            '_csrf': _csrf,
            'password': _encrypt_pwd,
            '_spring_security_remember_me': 'true'
        }

        res = self.session.post(login_api, data=data)
        bsobj = BeautifulSoup(res.text, 'lxml')
        if bsobj.select('.bbp-breadcrumb-root'):
            self.logger.info('登录成功！')
            nickname = bsobj.select('.bbp-breadcrumb-root')[0].get_text()
            self.logger.info('Hello, {}! '.format(nickname))
            self.redis_client.save_cookies(self.site, self.username, cookies)
            return cookies
        elif '用户名或密码错误' in res.text:
            self.reset_flag = True
            raise Exception('账号或密码错误! ')
        raise Exception('登录失败! ')

    @check_user()
    def run(self, load_cookies: bool = True):

        if load_cookies:
            cookies = self.redis_client.load_cookies(self.site, self.username)
            if cookies:
                if self.check_islogin(cookies):
                    return cookies
                self.logger.warning('Cookies 已过期')

        return self.login()


if __name__ == '__main__':
    x = OpenlawLogin().run()
    print(x)
