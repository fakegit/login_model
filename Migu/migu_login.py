# -*- coding: utf-8 -*-
# @Time    : 2019/7/25 18:35
# @Author  : Esbiya
# @Email   : 18829040039@163.com
# @File    : demo.py
# @Software: PyCharm


import execjs
from utils import *
import requests
import chardet
from bs4 import BeautifulSoup
from cookies_pool import RedisClient


class MiguLogin:

    def __init__(self, username: str = None, password: str = None):
        self.site = 'migu'
        self.logger = get_logger()
        self.username = username
        self.password = password
        self.redis_client = RedisClient(self.logger)
        self.session = requests.session()
        self.session.headers = {
            'Referer': 'https://passport.migu.cn/login?sourceid=220001&apptype=0&forceAuthn=false&isPassive=false&authType=MiguPassport&passwordControl=0&display=web&referer=http://music.migu.cn/v3&logintype=1&qq=null&weibo=null&alipay=null&weixin=null&phoneNumber=&callbackURL=http%3A%2F%2Fmusic.migu.cn%2Fv3&relayState=',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.80 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest'
        }
        # 密码错误重置初始化
        self.reset_flag = False
        self.ctx = self._load_js()

    def check_islogin(self, cookies):
        res = self.session.get('http://music.migu.cn/v3/my', cookies=cookies)
        html = res.content.decode(chardet.detect(res.content)['encoding'])
        if '我的收藏' in html:
            bsobj = BeautifulSoup(html, 'lxml')
            nickname = bsobj.find('h4', {'class': 'nickname'}).get_text().strip()
            self.logger.info('登录成功！')
            self.logger.info('Hello, {}! '.format(nickname))
            self.redis_client.save_cookies(self.site, self.username, cookies)
            return True
        return False

    def _load_js(self):
        """
        加载编译js文件
        :return:
        """
        with open('encrypt.js', 'rb') as f:
            js = f.read().decode()
        ctx = execjs.compile(js)
        return ctx

    def encrypt_pwd(self):
        """
        RSA加密密码
        :return:
        """
        encrypt_pwd = self.ctx.call('encryptPwd', self.password)
        # print('加密密码', encrypt_pwd)
        return encrypt_pwd

    def _get_fingerprint(self):
        """
        获取浏览器指纹
        :return:
        """
        finger_print = self.ctx.call('getFingerprint')
        # print('浏览器指纹', finger_print)
        return finger_print

    @loopUnlessSeccessOrMaxTry(3, sleep_time=3)
    def _get_token(self):
        """
        模拟登录
        :return:
        """
        login_api = 'https://passport.migu.cn/authn'

        data = {
            'sourceID': '220001',
            'appType': '0',
            'relayState': '',
            'loginID': self.username,
            'enpassword': self.encrypt_pwd(),
            'captcha': '',
            'imgcodeType': '1',
            'rememberMeBox': '1',
            'fingerPrint': self._get_fingerprint()['result'],
            'fingerPrintDetail': self._get_fingerprint()['details'],
            'isAsync': 'true'
        }

        res = self.session.post(login_api, data=data).json()
        if res['status'] == 2000:
            token = res['result']['token']
            return token
        elif res['message'] == '密码验证未通过' or res['message'] == '帐号或密码错误':
            self.reset_flag = True
            raise Exception('账号或密码错误! ')
        raise Exception('登录失败: ', res['message'])

    def login(self):
        """
        登录认证
        :return:
        """
        token = self._get_token()

        if token:
            params = {
                'callbackURL': '',
                'relayState': '',
                'token': token
            }

            res = self.session.get('http://music.migu.cn/v3/user/login?', params=params)
            cookies = res.cookies.get_dict()
            if self.check_islogin(cookies):
                return True
            return False

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
    MiguLogin().run(load_cookies=False)
