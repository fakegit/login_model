# -*- coding: utf-8 -*-
# @Time    : 2019/7/26 22:54
# @Author  : xuzhihai0723
# @Email   : 18829040039@163.com
# @File    : iQiyiLogin.py
# @Software: PyCharm

import execjs
import requests
import random
from utils import *
from bs4 import BeautifulSoup
from cookies_pool import RedisClient


class IQiyiLogin:

    def __init__(self, username: str = None, password: str = None):
        self.site = 'iqiyi'
        self.logger = get_logger()
        self.username = username
        self.password = password
        self.redis_client = RedisClient(self.logger)
        self.session = requests.session()
        self.session.headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Origin': 'http://www.iqiyi.com',
            'Referer': 'http://www.iqiyi.com/iframe/loginreg?ver=1',
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36"
        }
        # 密码错误重置初始化
        self.reset_flag = False

    def check_islogin(self, cookies):
        url = 'http://www.iqiyi.com/u/point'
        res = self.session.get(url, cookies=cookies)
        if 'ucbannerName' in res.text:
            self.logger.info('Cookies 有效! ')
            bsobj = BeautifulSoup(res.text, 'lxml')
            nickname = bsobj.select('#ucbannerName')[0].get_text().strip()
            self.logger.info('Hello, {}! '.format(nickname))
            return True
        return False

    def _encrypt_pwd(self):
        """
        加密密码
        :return:
        """
        with open('iqiyiPwdEncrypt.js', 'r') as f:
            js = f.read()

        ctx = execjs.compile(js)
        return ctx.call('rsaFun', self.password)

    def _get_areacode(self):
        """
        获取地区编码
        :return:
        """
        url = 'https://passport.iqiyi.com/apis/phone/get_support_areacode.action'
        data = {
            'use_case': '1',
            'local': '1',
            'agenttype': '1',
            'fromSDK': '1',
            'ptid': '01010021010000000000',
            'sdk_version': '1.0.0'
        }
        r = self.session.post(url, data=data).json()
        code_dict = r['data']['acode']
        return code_dict

    @loopUnlessSeccessOrMaxTry(3, sleep_time=3)
    def login(self):
        """
        登录, 只有一个加密参数密码, 其他为定值
        :return:
        """
        url = 'https://passport.iqiyi.com/apis/reglogin/login.action'

        encrypt_pwd = self._encrypt_pwd()

        data = {
            'email': self.username,
            'fromSDK': '1',
            'sdk_version': '1.0.0',
            'passwd': encrypt_pwd,
            'agenttype': '1',
            '__NEW': '1',
            'checkExist': '1',
            'lang': '',
            'ptid': '01010021010000000000',
            'nr': '1',
            'verifyPhone': '1',
            'area_code': '86',
            'env_token': 'c225a3e03fdf4c90a9227af2f0abd8bb',
            'dfp': 'a06e54c2dfe5d24ebf8aec1c2d0a8f5afb2fc70fd2a147f7ab9e5aea7cff440f9e',
            'envinfo': 'eyJqbiI6Ik1vemlsbGEvNS4wIChXaW5kb3dzIE5UIDEwLjA7IFdPVzY0OyBydjo2Ny4wKSBHZWNrby8yMDEwMDEwMSBGaXJlZm94LzY3LjAiLCJjbSI6InpoLUNOIiwiZ3UiOjI0LCJ1ZiI6MSwianIiOlsxMzY2LDc2OF0sImRpIjpbMTM2Niw3MjhdLCJ6cCI6LTQ4MCwidWgiOjEsInNoIjoxLCJoZSI6MSwicnYiOiJ1bmtub3duIiwibngiOiJXaW4zMiIsIml3IjoidW5zcGVjaWZpZWQiLCJxbSI6W10sIndyIjoiOWUzYjk5MzFhNzBiMGQwZDI0NGU1ZTg1MTAyZGJiYTAiLCJ3ZyI6IjRlMzVhYWVjZTM2NTU0YTM5MGQwYWU1MDNlZDljOTM0IiwiZmsiOmZhbHNlLCJyZyI6ZmFsc2UsInh5IjpmYWxzZSwiam0iOmZhbHNlLCJiYSI6ZmFsc2UsInRtIjpbMCxmYWxzZSxmYWxzZV0sImF1Ijp0cnVlLCJtaSI6IjQ1MjY1MDUxLWM3MjItNTcyOC00OGY3LWJiMjA3N2NlMGVhMCIsImNsIjoiUENXRUIiLCJzdiI6IjEuMCIsImpnIjoiNTE3YzNiNDk0NzFlMTJiZTc0N2QzYWI3MWY1YTM1OTMiLCJmaCI6ImhydWtvdjY0OW15OGV1YnB4Ym9uMThuayIsImlmbSI6W3RydWUsNDYwLDQyMCwiaHR0cDovL3d3dy5pcWl5aS5jb20vIl0sImV4IjoiIiwicHYiOmZhbHNlfQ=='
        }

        while True:
            res = self.session.post(url, data=data)
            cookies = res.cookies.get_dict()
            if res.json()['code'] == 'A00000':
                self.logger.info('登录成功! ')
                self.logger.info('Hello, {}! '.format(res.json()['data']['nickname']))
                self.redis_client.save_cookies(self.site, self.username, cookies)
                return True
            elif res.json()['code'] == 'P00117':
                self.reset_flag = True
                raise Exception('账号或密码错误! ')
            token = res.json()['data']['data']['token']
            data.update({'env_token': token})
            self.logger.info(f'{res.json()["msg"]}, env_token更新为: {token}')
            time.sleep(random.random())

    def get_userinfo(self, cookies):
        """
        获取用户信息
        :return:
        """
        url = 'https://passport.iqiyi.com/apis/user/info.action'
        code_dict = self._get_areacode()
        with open('antiCsrf.js', 'rb') as f:
            js = f.read().decode()
        ctx = execjs.compile(js)

        try:
            auth_cookie = cookies['P00001']
            anticsrf = ctx.call('getAnticsrf', auth_cookie)

            data = {
                'agenttype': '1',
                'ptid': '01010021010000000000',
                'lang': '',
                'fromSDK': '1',
                'sdk_version': '1.0.0',
                'authcookie': auth_cookie,
                'antiCsrf': anticsrf,
                'fields': 'insecure_account,userinfo'
            }

            r = requests.post(url, data=data)
            user_info = r.json()['data']['userinfo']
            jointime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(user_info['jointime'])))
            if user_info['gender'] == 1:
                gender = '男'
            else:
                gender = '女'
            area_code = user_info['area_code']
            for code in code_dict.keys():
                if area_code == code:
                    area = code_dict[code]
                    if user_info['birthday']:
                        birthday = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(user_info['birthday'])))
                        user_info.update({'birthday': birthday, 'jointime': jointime, 'gender': gender, 'area': area})
            # 移除地区代码
            del user_info['area_code']
            self.logger.info(f'您的基本信息为: {user_info}')
            return True
        except:
            return False

    @check_user()
    def run(self, load_cookies: bool = True):
        """
        主函数
        :return:
        """
        if load_cookies:
            cookies = self.redis_client.load_cookies(self.site, self.username)
            if cookies:
                if self.check_islogin(cookies):
                    info_flag = input('是否显示用户信息? (yes/no) \n')
                    if info_flag == 'yes':
                        self.get_userinfo(cookies)
                    return True
                self.logger.warning('Cookies 已过期')

        self.login()


if __name__ == '__main__':
    IQiyiLogin().run(load_cookies=False)
