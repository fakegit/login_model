# -*- coding: utf-8 -*-
# @Time    : 2019/7/25 16:23
# @Author  : Esbiya
# @Email   : 18829040039@163.com
# @File    : login.py
# @Software: PyCharm


import requests
from chaojiying import image_to_text
import execjs
import chardet
from utils import *
from cookies_pool import RedisClient
from urllib.parse import urlencode


class QimaiLogin:

    def __init__(self, username: str = None, password: str = None):
        self.site = 'qimai'
        self.logger = get_logger()
        self.username = username
        self.password = password
        self.redis_client = RedisClient(self.logger)
        self.session = requests.session()
        self.session.headers = {
            'Accept': 'application/json, text/plain, */*',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Origin': 'https://www.qimai.cn',
            'Referer': 'https://www.qimai.cn/account/signin/r/%2Frank%2Findex%2Fbrand%2Ffree%2Fcountry%2Fcn%2Fgenre%2F5000%2Fdevice%2Fiphone',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.80 Safari/537.36'
        }

        # 密码错误重置初始化
        self.reset_flag = False

    def check_islogin(self, cookies):
        url = 'https://api.qimai.cn/account/settingAccount?analysis=eEcbVwJTX0VeRB9DXRBDUQpTdwJTX0VeRHATFVUCCVEFBFQEAAgGAgFwG1U%3D'
        res = self.session.get(url, cookies=cookies).json()
        if res['code'] == 10000 and res['msg'] == '成功':
            self.logger.info('登录成功！')
            self.logger.info('Hello, {}! '.format(res['accountInfo']['realname']))
            self.redis_client.save_cookies(self.site, self.username, cookies)
            return True
        return False

    @loopUnlessSeccessOrMaxTry(3, sleep_time=3)
    def _get_verifycode(self):
        timestamp = int(time.time() * 1000)
        captcha_url = f'https://api.qimai.cn/account/getVerifyCodeImage?{timestamp}'
        img_data = self.session.get(captcha_url).content
        self.logger.info('使用超级鹰识别验证码...')
        ok, result = image_to_text(img_data)
        if ok:
            self.logger.info('成功识别验证码！')
            return result
        raise Exception('验证码识别失败: ', result)

    def _get_synct(self):
        resp = self.session.get('https://www.qimai.cn/rank')
        cookies = resp.cookies.get_dict()
        return cookies.get('synct')

    @staticmethod
    def _get_analysis(synct):
        with open('analysis.js', 'rb') as f:
            js = f.read().decode()
        ctx = execjs.compile(js)
        return ctx.call('getLoginAnalysis', synct)

    @loopUnlessSeccessOrMaxTry(3, sleep_time=3)
    def login(self, login_api):
        data = {
            'username': self.username,
            'password': self.password,
            'code': self._get_verifycode()
        }
        res = self.session.post(login_api, data=data)
        cookies = res.cookies.get_dict()
        if self.check_islogin(cookies):
            return True
        elif res.json()['msg'] == '用户名或密码错误':
            self.reset_flag = True
            raise Exception('账号或密码错误! ')
        raise Exception('登录失败: ', res.json()['msg'])

    @check_user()
    def run(self, load_cookies: bool = True):
        """
        模拟登录
        :param load_cookies:
        :return:
        """
        synct = self._get_synct()
        url = 'https://api.qimai.cn/account/signinForm?'
        params = {
            'analysis': self._get_analysis(synct)
        }
        login_api = url + urlencode(params)
        if load_cookies:
            cookies = self.redis_client.load_cookies(self.site, self.username)
            if cookies:
                if self.check_islogin(cookies):
                    return True
                self.logger.warning('Cookies 已过期')

        self.login(login_api)


if __name__ == '__main__':
    QimaiLogin().run(load_cookies=False)
