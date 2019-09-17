# -*- coding: utf-8 -*-
# @Time    : 2019/7/29 21:08
# @Author  : xuzhihai0723
# @Email   : 18829040039@163.com
# @File    : qichamao_login.py
# @Software: PyCharm

import requests
from bs4 import BeautifulSoup
from utils import *
from chaojiying import image_to_text
from cookies_pool import RedisClient


class QichamaoLogin:

    def __init__(self, username: str = None, password: str = None):
        self.site = 'qichamao'
        self.username = username
        self.password = password
        self.logger = get_logger()
        self.redis_client = RedisClient(self.logger)
        self.session = requests.session()
        self.session.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.80 Safari/537.36'
        }

        # 密码错误重置
        self.reset_flag = True

    @loopUnlessSeccessOrMaxTry(3, sleep_time=3)
    def _get_verifycode(self):
        captcha_url = 'https://www.qichamao.com/usercenter/varifyimage?'
        img_data = self.session.get(captcha_url).content
        self.logger.info('使用超级鹰识别验证码...')
        ok, result = image_to_text(img_data)
        if ok:
            self.logger.info('成功识别验证码！')
            return result
        raise Exception('验证码识别失败: ', result)

    def check_islogin(self, cookies):
        """
        检查登录状态，访问登录页面跳转则是已登录，
        如登录成功保存当前 Cookies
        :return: bool
        """
        login_url = 'https://www.qichamao.com/usercenter/login'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 Edge/16.16299'
        }
        resp = requests.get(login_url, cookies=cookies, headers=headers)
        if 'userhd_name' in resp.text:
            self.logger.info('登录成功! ')
            bsobj = BeautifulSoup(resp.text, 'lxml')
            nickname = bsobj.select('.userhd_name')[0].get_text()
            self.logger.info('Hello, {}! '.format(nickname))
            self.redis_client.save_cookies(self.site, self.username, cookies)
            return True
        return False

    @loopUnlessSeccessOrMaxTry(3, sleep_time=3)
    def login(self):
        login_api = 'https://www.qichamao.com/usercenter/dologin'

        verify_code = self._get_verifycode()
        data = {
            'userId': self.username,
            'password': self.password,
            'VerifyCode': verify_code,
            'sevenDays': 'false'
        }
        res = self.session.post(login_api, data=data)
        cookies = res.cookies.get_dict()
        if self.check_islogin(cookies):
            return True
        elif '用户名或密码错误' in res.json()['sMsg']:
            raise Exception('账号或密码错误! ')
        raise Exception(json.loads(res.text)['sMsg'])

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
    QichamaoLogin().run(load_cookies=True)
