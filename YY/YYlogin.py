# -*- coding: utf-8 -*-
# @Time    : 2019/7/4 21:45
# @Author  : Esbiya
# @Email   : 18829040039@163.com
# @File    : YYlogin.py
# @Software: PyCharm

import re
import random
import requests
import execjs
from utils import *
from cookies_pool import RedisClient


class YYlogin:

    def __init__(self, username: str = None, password: str = None):
        self.site = 'yy'
        self.username = username
        self.password = password
        self.logger = get_logger()
        self.redis_client = RedisClient(self.logger)
        self.session = requests.session()
        self.session.headers = {
            'Referer': 'http://www.yy.com/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:68.0) Gecko/20100101 Firefox/68.0'
        }
        # 密码错误重置初始化
        self.reset_flag = False

    def check_islogin(self, cookies):
        url = 'http://www.yy.com/yyweb/user/queryUserInfo.json??callback=jQuery1111045940186663574223_{}'.format(
            int(time.time() * 1000))
        res = self.session.get(url, cookies=cookies).json()
        if res['resultCode'] == 0:
            self.logger.info('Cookies 有效! ')
            self.logger.info('Hello, {}! '.format(res['data']['nick']))
            return True
        return False

    def _init_cookies(self):
        self.session.get('http://www.yy.com/')

    def _get_url(self):
        while True:
            url = 'http://www.yy.com/login/getSdkAuth?embed=true&cssid=5719_1'
            res = self.session.post(url).json()
            if res['success'] == 1:
                ttokensec = res['ttokensec']
                token_url = res['url']
                return ttokensec, token_url
            time.sleep(random.random())

    def _get_token(self, url):
        res = self.session.get(url)
        oauth_token = re.search('oauth_token: "(.*?)"', res.text, re.S).group(1)
        return oauth_token

    def _encrypt_pwd(self):
        with open('encrypt.js', 'rb') as f:
            js = f.read().decode()

        ctx = execjs.compile(js)
        return ctx.call('encryptPwd', self.password)

    def _get_captcha(self, captcha_id):
        base_url = 'https://captcha.yy.com/pickwords/init.do?'
        params = {
            'appid': 5719,
            'random': int(time.time() * 1000),
            'busiId': 'busiid',
            'captchaId': captcha_id,
            'callback': f'JSONP_{int(time.time() * 1000)}'
        }
        res = self.session.get(base_url, params=params)
        with open('captcha.png', 'wb') as f:
            f.write(res.content)
        # img = Image.open('captcha.png')
        # img.show()

    @loopUnlessSeccessOrMaxTry(3, sleep_time=3)
    def login(self):
        login_api = 'https://lgn.yy.com/lgn/oauth/x2/s/login_asyn.do'

        self._init_cookies()
        ttokensec, token_url = self._get_url()
        oauth_token = self._get_token(token_url)
        pwd = self._encrypt_pwd()
        data = {
            'username': self.username,
            'pwdencrypt': pwd,
            'oauth_token': oauth_token,
            'denyCallbackURL': 'http://www.yy.com/login/udbCallback?cancel=1',
            'UIStyle': 'xelogin',
            'appid': 5719,
            'cssid': 5719_1,
            'mxc': '',
            'vk': '',
            'isRemMe': '1',
            'mmc': '',
            'vv': '',
            'hiido': '1'
        }
        res = requests.post(login_api, data=data).json()

        if res['code'] == '0':
            callback_url = res['obj']['callbackURL']
            r_cookies = {"_pwcWyy": "066696ef76ca2f85", "cookieDate": "1564841513462", "hd_newui": "0.970057832001334",
                         "hdjs_session_id": "0.5300241632973548", "hdjs_session_time": "1564842336414",
                         "hiido_ui": "0.7355867355495954", "Hm_lpvt_c493393610cdccbddc1f124d567e36ab": "1564842337",
                         "Hm_lvt_c493393610cdccbddc1f124d567e36ab": "1564841491,1564841511,1564842337",
                         "udboauthtmptoken": "undefined", "udboauthtmptokensec": ttokensec}
            resp = self.session.get(callback_url, cookies=r_cookies)

            if 'loginSuccess' in resp.text:
                final_url = re.search(r"writeCrossmainCookieWithCallBack\('(.*?)',", resp.text).group(1)
                response = self.session.get(final_url)
                if 'write cookie for oauth' in response.text:
                    self.logger.info('登录成功！')
                    cookies = response.cookies.get_dict()
                    self.redis_client.save_cookies(self.site, self.username, cookies)
                    return cookies
            raise Exception('登录失败! ')
        elif res['code'] == '1000010':
            self.reset_flag = True
            raise Exception('账号或密码错误！ ')
        elif res['code'] == '1000001':
            self.logger.warning(res['msg'])
            captcha_id = re.search('captchaId: "(.*?)",', res['obj']['itvjs'], re.S).group(1)
            self._get_captcha(captcha_id)
        elif res['code'] == '1000003':
            self.logger.warning(res['msg'])
            return None
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
    x = YYlogin().run(load_cookies=True)
    print(x)
