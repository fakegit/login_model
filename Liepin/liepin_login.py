# -*- coding: utf-8 -*-
# @Time    : 2019/7/25 22:34
# @Author  : Esbiya
# @Email   : 18829040039@163.com
# @File    : iQiyiLogin.py
# @Software: PyCharm

import requests
import execjs
import re
import json
from utils import *
from cookies_pool import RedisClient
import hashlib


class LiepinLogin:

    def __init__(self, username: str = None, password: str = None):
        self.site = 'liepin'
        self.logger = get_logger()
        self.username = username
        self.password = password
        self.redis_client = RedisClient(self.logger)
        self.session = requests.session()
        self.session.headers = {
            'Referer': 'https://www.liepin.com/',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36',
            'DNT': '1',
        }
        # 密码错误重置初始化
        self.reset_flag = False
        self.timestamp = str(int(time.time() * 1000))

    def check_islogin(self, cookies):
        url = 'https://c.liepin.com/main/page.json?'
        res = self.session.get(url, cookies=cookies, allow_redirects=False)
        try:
            result = json.loads(res.text)
            if result['status'] == 0 and result['message'] == 'OK':
                self.logger.info('登录成功！')
                self.logger.info('Hello, {}! '.format(result['data']['userCForm']['c_name']))
                self.redis_client.save_cookies(self.site, self.username, cookies)
                return True
        except:
            return False

    @staticmethod
    def _loads_jsonp(_jsonp):
        """
        解析jsonp数据格式为json
        :return:
        """
        try:
            return json.loads(re.match(".*?({.*}).*", _jsonp, re.S).group(1))
        except ValueError:
            raise ValueError('Invalid Input')

    def _get_token(self):
        """
        获取用户token和加密js
        :return:
        """

        params = {
            'sign': self.username,
            'callback': 'jQuery171029989774566236793_' + self.timestamp,
            '_': self.timestamp,
        }

        response = self.session.get('https://passport.liepin.com/verificationcode/v1/js.json', params=params)

        return self._loads_jsonp(response.text)

    def _encrypt_pwd(self):
        md5 = hashlib.md5()
        md5.update(self.password.encode('utf-8'))
        return md5.hexdigest()

    @loopUnlessSeccessOrMaxTry(3, sleep_time=3)
    def login(self):
        """
        模拟登录
        :return:
        """
        result = self._get_token()
        token = result.get('data').get('token')
        js = result.get('data').get('js')

        ctx = execjs.compile(js)
        value = ctx.call('encryptData', self.username)

        pwd = self._encrypt_pwd()

        params = {
            'callback': 'jQuery17108618602708711502_' + self.timestamp,
            'login': self.username,
            'pwd': pwd,
            'token': token,
            'value': value,
            'url': '',
            '_bi_source': '0',
            '_bi_role': '0',
            '_': self.timestamp,
        }

        res = self.session.get('https://passport.liepin.com/account/individual/v1/login.json', params=params)
        cookies = res.cookies.get_dict()
        result = json.loads(re.search(f'{params["callback"]}\((.*)\)', res.text).group(1))
        if self.check_islogin(cookies):
            return True
        if '密码错误' in res.text:
            self.reset_flag = True
            raise Exception('账号或密码错误! ')
        raise Exception('登录失败: {}'.format(result['msg']))

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
    LiepinLogin().run(load_cookies=True)
