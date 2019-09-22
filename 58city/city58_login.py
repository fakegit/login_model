# -*- coding: utf-8 -*-
# @Time    : 2019/7/2 16:42
# @Author  : Esbiya
# @Email   : 18829040039@163.com
# @File    : login.py
# @Software: PyCharm

"""
登录次数不多时可以成功登录, 测试时多次登录导致账号异常: 您的账号存在安全风险，需要验证手机号
"""

import requests
import json
import execjs
import re
from urllib.parse import unquote
import getpass
from utils import *
import time
from cookies_pool import RedisClient
from pyquery import PyQuery as pq


class City58Login:

    def __init__(self, username: str = None, password: str = None):
        self.site = '58city'
        self.logger = get_logger()
        self.username = username
        self.password = password
        self.redis_client = RedisClient(self.logger)
        self.session = requests.session()
        self.session.headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.80 Safari/537.36'
        }
        # 密码错误重置初始化
        self.reset_flag = False

    def _get_token(self):
        """
        获取登录的token参数
        :return:
        """
        base_url = 'https://passport.58.com/sec/58/feature/pc/ui?'
        res = self.session.get(base_url)
        doc = pq(res.text)
        path = doc('#path').attr('value')
        timestamp = int(time.time()*1000)
        url = f'https://passport.58.com/58/login/init?callback=jQuery112401218021763208601_{timestamp}&source=58-default-pc&path={path}&psdk-d=jsdk&psdk-v=1.0.0&_={int(time.time()*1000)}'
        r = self.session.get(url)
        result = json.loads(r.text.replace(f'jQuery112401218021763208601_{timestamp}(', '').replace(')', ''))
        token = result['data']['token']
        return path, token

    def _encrypt_pwd(self):
        """
        RSA加密密码
        :return:
        """
        with open('encrypt.js', 'rb') as f:
            js = f.read().decode()
        ctx = execjs.compile(js)
        encrypt_pwd = ctx.call('encryptString', self.password)
        return encrypt_pwd

    def check_islogin(self, cookies):
        """
        检查是否成功登录
        :return:
        """
        url = 'http://my.58.com/webpart/userbasicinfo?'
        res = self.session.get(url, cookies=cookies)
        if 'username' in res.text:
            self.logger.info('Cookies 有效!')
            nickname = unquote(cookies['58uname'])
            self.logger.info('Hello, {}! '.format(nickname))
            self.redis_client.save_cookies(self.site, self.username, cookies)
            return True
        return False

    @loopUnlessSeccessOrMaxTry(3, sleep_time=3)
    def login(self):
        """
        登录
        :return:
        """
        login_api = 'https://passport.58.com/58/login/pc/dologin'

        encrypt_pwd = self._encrypt_pwd()
        path, token = self._get_token()
        # 浏览器指纹可固定
        data = {
            'fingerprint': 'cFJ17E_h2J-JDePNDcjQipipJf-ulq8O',
            'callback': 'successFun',
            'username': self.username,
            'password': encrypt_pwd,
            'token': token,
            'source': '58-default-pc',
            'path': path,
            'domain': '58.com',
            'finger2': 'zh-CN|24|1|4|1366_768|1366_728|-480|1|1|1|undefined|1|unknown|Win32|unknown|3|false|false|false|false|false|0_false_false|d41d8cd98f00b204e9800998ecf8427e|ab307cc3fc702e5ba66265525bf235e9',
            'psdk-d': 'jsdk',
            'psdk-v': '1.0.0'
        }
        self.session.headers.update(
            {
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
                'accept-encoding': 'gzip, deflate, br',
                'accept-language': 'zh-CN,zh;q=0.9',
                'cache-control': 'max-age=0',
                'content-length': '918',
                'content-type': 'application/x-www-form-urlencoded',
                'cookie': 'id58=c5/njVzb4POxn3A0A5HAAg==; 58tj_uuid=d9c75b22-75df-45a5-9753-7d50573ecf07; als=0; xxzl_deviceid=q7tLhmL5%2BD1rBg1ATI6k4pOMk5JPQohVW%2F2gGSVpM6FQmGsn62qCn5qWyuyKi9WD; wmda_uuid=241b006d58daf7ba9c3bb7e99a44dc04; wmda_new_uuid=1; wmda_visited_projects=%3B2385390625025; ppStore_fingerprint=2435661B36DB2AADF42830177DB0924E0018B24F3003A472%EF%BC%BF1557913861099; 58home=hf; city=hf; mcity=hf; finger_session=cFJ17E_h2J-JDePNDcjQipipJf-ulq8O; new_session=1; new_uv=6; utm_source=sem-sales-360-pc; spm=18470355416.%7Bcreative%7D; init_refer=https%253A%252F%252Fwww.so.com%252Fs%253Fie%253Dutf-8%2526src%253Ddlm%2526shb%253D1%2526hsid%253D048b900bc5158a43%2526ls%253Dn5eecf99698%2526q%253D58%2525E5%252590%25258C%2525E5%25259F%25258E',
                'origin': 'https://passport.58.com',
                'referer': 'https://passport.58.com/login/?path=https%3A//hf.58.com/chuzu/%3Futm_source%3Dsem-sales-360-pc%26spm%3D18470355416.%7Bcreative%7D%26utm_campaign%3Dsell%26utm_medium%3Dcpc%26showpjs%3Dpc_fg&PGTID=0d3090a7-0034-5e39-c90b-41d899bb8a55&ClickID=2',
                'upgrade-insecure-requests': '1',
            }
        )
        resp = self.session.post(login_api, data=data)
        doc = pq(resp.text)
        result = json.loads(re.search(r'parent.successFun\((.*?)\)', doc('script').text()).group(1))
        if result['code'] == 0:
            self.logger.info('登录成功! ')
            cookies = resp.cookies.get_dict()
            nickname = unquote(cookies['58uname'])
            self.logger.info('Hello, {}! '.format(nickname))
            self.redis_client.save_cookies(self.site, self.username, cookies)
            return cookies
        elif result['msg'] == '该用户名与密码不符' or result['msg'] == '密码格式错误，请重置':
            self.reset_flag = True
            raise Exception('账号或密码错误! ')
        # 手机号验证...
        raise Exception('登录失败: {} '.format(result['msg']))

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
    x = City58Login().run()
    print(x)
