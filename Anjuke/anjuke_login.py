# -*- coding: utf-8 -*-
# @Time    : 2019/8/7 17:23
# @Author  : xuzhihai0723
# @Email   : 18829040039@163.com
# @File    : anjuke_login.py
# @Software: PyCharm

import requests
import re
import hashlib
from bs4 import BeautifulSoup
from urllib.parse import urlencode
from utils import *
from chaojiying import image_to_text
from cookies_pool import RedisClient


class AnjukeLogin:

    def __init__(self, username: str = None, password: str = None):
        self.site = 'anjuke'
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
        res = self.session.get('https://user.anjuke.com/user/profile', cookies=cookies)
        if 'user-account' in res.text:
            bsobj = BeautifulSoup(res.text, 'lxml')
            nickname = bsobj.select('.user-account span')[0].get_text()
            self.logger.info('Cookies 有效! ')
            self.logger.info(f'Hello, {nickname}! ')
            return True
        return False

    def init(self):
        """
        初始化 cookies, 并获取加密方式和加密 token
        :return:
        """
        url = 'https://login.anjuke.com/login/iframeform?style=1&forms=11&third_parts=111&other_parts=111&history=aHR0cHM6Ly9oZi5hbmp1a2UuY29tLw%3D%3D&check_bind_phone=1'
        resp = self.session.get(url)
        bsobj = BeautifulSoup(resp.text, 'lxml')
        alog = re.search('algo.*?: "(.*?)"', resp.text, re.S).group(1)
        history = bsobj.select('input[name="history"]')[0]['value']
        token = bsobj.select('input[name="token"]')[0]['value']
        return alog, history, token

    @staticmethod
    def md5(token):
        encrypter = hashlib.md5()
        encrypter.update(token)
        return encrypter.hexdigest()

    @staticmethod
    def sha1(token):
        encrypter = hashlib.sha1()
        encrypter.update(token)
        return encrypter.hexdigest()

    @staticmethod
    def sha256(token):
        encrypter = hashlib.sha256()
        encrypter.update(token)
        return encrypter.hexdigest()

    def _get_token2(self, algo, token):
        if algo == 'algo1':
            return self.md5(token)
        elif algo == 'algo2':
            return self.sha1(token)
        elif algo == 'algo3':
            return self.sha256(token)
        elif algo == 'algo4':
            token_ = self.md5(token)
            return self.sha1(token_.encode())
        elif algo == 'algo5':
            token_ = self.sha1(token)
            return self.sha256(token_.encode())

    def _check_risk(self):
        """
        判断是否需要验证码
        :return:
        """
        url = 'https://login.anjuke.com/login/checkshowcaptcha?account={}'.format(self.username)
        resp = self.session.get(url).json()
        if resp['code'] == 10005:
            self.logger.warning(resp['msg'])
            return True
        return False

    def _get_verifycode(self):
        captcha_url = 'https://login.anjuke.com/general/captcha?h=45&timestamp={}'.format(int(time.time()) * 1000)
        img_data = self.session.get(captcha_url).content
        self.logger.info('使用超级鹰识别验证码...')
        ok, result = image_to_text(img_data)
        if ok:
            self.logger.info('成功识别验证码！')
            return result
        raise Exception('验证码识别失败: ', result)

    @loopUnlessSeccessOrMaxTry(3, sleep_time=3)
    def login(self):
        login_api = 'https://login.anjuke.com/login/submit?hidehead=0'

        algo, history, token = self.init()
        token2 = self._get_token2(algo, token.encode())
        flag = self._check_risk()
        if flag:
            verifycode = self._get_verifycode()
        else:
            verifycode = ''

        data = {
            'username': self.username,
            'password': self.password,
            'captcha': verifycode,
            'style': '1',
            'third_parts': '111',
            'other_parts': '111',
            'forms': '11',
            'login_type': '2',
            'history': history,
            'check_bind_phone': '1',
            'token': token,
            'token2': token2,
            'multi_form': '0'
        }

        resp = self.session.post(login_api, data=data)
        if 'loginSuccess' in resp.text:
            self.logger.info('登录成功! ')
            self.session.get('https://hf.anjuke.com/')
            cookies = self.session.cookies.get_dict()
            self.redis_client.save_cookies(self.site, self.username, cookies)
            return True
        elif 'errorItemTopPwd' in resp.text:
            bsobj = BeautifulSoup(resp.text, 'lxml')
            reason = bsobj.select('#errorItemTopPwd')[0].get_text()
            if reason == '用户名或密码错误':
                self.reset_flag = True
                raise Exception('账号或密码错误! ')
            raise Exception(reason)
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
    AnjukeLogin().run(load_cookies=False)
