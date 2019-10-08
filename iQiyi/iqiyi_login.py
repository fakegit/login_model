# -*- coding: utf-8 -*-
# @Time    : 2019/7/26 22:54
# @Author  : Esbiya
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

    def get_dfp(self):
        """
        获取页面初始化参数 dfp
        :return:
        """
        url = 'https://cook.iqiyi.com/security/dfp_pcw/sign'

        data = {
            'dim': 'eyJqbiI6Ik1vemlsbGEvNS4wIChXaW5kb3dzIE5UIDEwLjA7IFdpbjY0OyB4NjQpIEFwcGxlV2ViS2l0LzUzNy4zNiAoS0hUTUwsIGxpa2UgR2Vja28pIENocm9tZS83NS4wLjM3NzAuODAgU2FmYXJpLzUzNy4zNiIsImNtIjoiemgtQ04iLCJndSI6MjQsInVmIjoxLCJqciI6WzEzNjYsNzY4XSwiZGkiOlsxMzY2LDcyOF0sInpwIjotNDgwLCJ1aCI6MSwic2giOjEsImhlIjoxLCJ6byI6MSwicnYiOiJ1bmtub3duIiwibngiOiJXaW4zMiIsIml3IjoidW5rbm93biIsInFtIjpbIkNocm9tZSBQREYgUGx1Z2luOjpQb3J0YWJsZSBEb2N1bWVudCBGb3JtYXQ6OmFwcGxpY2F0aW9uL3gtZ29vZ2xlLWNocm9tZS1wZGZ cGRmIiwiQ2hyb21lIFBERiBWaWV3ZXI6Ojo6YXBwbGljYXRpb24vcGRmfnBkZiIsIk5hdGl2ZSBDbGllbnQ6Ojo6YXBwbGljYXRpb24veC1uYWNsfixhcHBsaWNhdGlvbi94LXBuYWNsfiJdLCJ3ciI6ImI3NzY2NGM3MTcwNzdhZmZmMzNhN2QyODM2ZTIzNzdjIiwid2ciOiJlZDI2NTg5MTM1MTJlNTA5MmZlMjE5NDAwOGQ3OWEwZSIsImZrIjpmYWxzZSwicmciOmZhbHNlLCJ4eSI6ZmFsc2UsImptIjpmYWxzZSwiYmEiOmZhbHNlLCJ0bSI6WzAsZmFsc2UsZmFsc2VdLCJhdSI6dHJ1ZSwibWkiOiI5YmU0OTM0MS05MTI2LTg5MjQtNjc2Ni0xOTA3Y2QxNTYxMDgiLCJjbCI6IlBDV0VCIiwic3YiOiIxLjAiLCJqZyI6IjA3NjQ4M2QwODg2NGMzNTE5MWUyNTVjNjhmNWU2YWE3IiwiZmgiOiJvazZxeWc0cXM5YWw5MTA0YjZ0OTJoODEiLCJpZm0iOltmYWxzZSxudWxsLG51bGwsbnVsbF0sImV4IjoiIiwiZHYiOiJvZmYiLCJwdiI6dHJ1ZX0=',
            'plat': 'PCWEB',
            'ver': '1.0',
            'sig': '785042546DC84608E1DF7430A9AE021C2F6F7955',
            'nifc': 'false'
        }
        result = self.session.post(url, data=data).json()
        if result['code'] == 0:
            dfp = result['result']['dfp']
            print('dfp: {}'.format(dfp))
            print('{} 后过期'.format(result['result']['expireAt'] - int(time.time() * 1000)))
            return dfp
        return None

    @loopUnlessSeccessOrMaxTry(3, sleep_time=3)
    def login(self):
        """
        登录, 只有一个加密参数密码, 其他为定值
        :return:
        """
        url = 'https://passport.iqiyi.com/apis/reglogin/login.action'

        encrypt_pwd = self._encrypt_pwd()

        dfp = self.get_dfp()
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
            # 'env_token': 'c225a3e03fdf4c90a9227af2f0abd8bb',
            'dfp': dfp,
            'envinfo': 'eyJqbiI6Ik1vemlsbGEvNS4wIChXaW5kb3dzIE5UIDEwLjA7IFdpbjY0OyB4NjQpIEFwcGxlV2ViS2l0LzUzNy4zNiAoS0hUTUwsIGxpa2UgR2Vja28pIENocm9tZS83NS4wLjM3NzAuODAgU2FmYXJpLzUzNy4zNiIsImNtIjoiemgtQ04iLCJndSI6MjQsInVmIjoxLCJqciI6WzEzNjYsNzY4XSwiZGkiOlsxMzY2LDcyOF0sInpwIjotNDgwLCJ1aCI6MSwic2giOjEsImhlIjoxLCJ6byI6MSwicnYiOiJ1bmtub3duIiwibngiOiJXaW4zMiIsIml3IjoidW5rbm93biIsInFtIjpbIkNocm9tZSBQREYgUGx1Z2luOjpQb3J0YWJsZSBEb2N1bWVudCBGb3JtYXQ6OmFwcGxpY2F0aW9uL3gtZ29vZ2xlLWNocm9tZS1wZGZ cGRmIiwiQ2hyb21lIFBERiBWaWV3ZXI6Ojo6YXBwbGljYXRpb24vcGRmfnBkZiIsIk5hdGl2ZSBDbGllbnQ6Ojo6YXBwbGljYXRpb24veC1uYWNsfixhcHBsaWNhdGlvbi94LXBuYWNsfiJdLCJ3ciI6ImI3NzY2NGM3MTcwNzdhZmZmMzNhN2QyODM2ZTIzNzdjIiwid2ciOiJlZDI2NTg5MTM1MTJlNTA5MmZlMjE5NDAwOGQ3OWEwZSIsImZrIjpmYWxzZSwicmciOmZhbHNlLCJ4eSI6ZmFsc2UsImptIjpmYWxzZSwiYmEiOmZhbHNlLCJ0bSI6WzAsZmFsc2UsZmFsc2VdLCJhdSI6dHJ1ZSwibWkiOiI5YmU0OTM0MS05MTI2LTg5MjQtNjc2Ni0xOTA3Y2QxNTYxMDgiLCJjbCI6IlBDV0VCIiwic3YiOiIxLjAiLCJqZyI6IjA3NjQ4M2QwODg2NGMzNTE5MWUyNTVjNjhmNWU2YWE3IiwiZmgiOiJvazZxeWc0cXM5YWw5MTA0YjZ0OTJoODEiLCJpZm0iOltmYWxzZSxudWxsLG51bGwsbnVsbF0sImV4IjoiIiwiZHYiOiJvZmYiLCJwdiI6dHJ1ZX0='
        }

        while True:
            res = self.session.post(url, data=data)
            cookies = res.cookies.get_dict()
            if res.json()['code'] == 'A00000':
                self.logger.info('登录成功! ')
                self.logger.info('Hello, {}! '.format(res.json()['data']['nickname']))
                self.redis_client.save_cookies(self.site, self.username, cookies)
                return cookies
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
                    return cookies
                self.logger.warning('Cookies 已过期')

        return self.login()


if __name__ == '__main__':
    x = IQiyiLogin().run(load_cookies=False)
    print(x)