# -*- coding: utf-8 -*-
# @Time    : 2019/9/19 13:17
# @Author  : Esbiya
# @Email   : 18829040039@163.com
# @File    : meituan_login_js.py
# @Software: PyCharm

import execjs
from bs4 import BeautifulSoup
import re
from utils import *
from cookies_pool import RedisClient
from PIL import Image
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import requests


class MeituanLogin:

    def __init__(self, username: str = None, password: str = None):
        self.site = 'meituan'
        self.username = username
        self.password = password
        self.logger = get_logger()
        self.redis_client = RedisClient(self.logger)

        self.session = requests.session()
        self.session.headers = {
            'Referer': 'https://epassport.meituan.com/account/unitivelogin?bg_source=3&service=waimai&platform=2&continue=http://e.waimai.meituan.com/v2/epassport/entry&left_bottom_link=%2Faccount%2Funitivesignup%3Fbg_source%3D3%26service%3Dwaimai%26platform%3D2%26continue%3Dhttp%3A%2F%2Fe.waimai.meituan.com%2Fv2%2Fepassport%2FsignUp%26extChannel%3Dwaimaie%26ext_sign_up_channel%3Dwaimaie&right_bottom_link=%2Faccount%2Funitiverecover%3Fbg_source%3D3%26service%3Dwaimai%26platform%3D2%26continue%3Dhttp%3A%2F%2Fe.waimai.meituan.com%2Fv2%2Fepassport%2FchangePwd',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
        }
        with open('./js/encrypt_pwd.js', 'rb') as f:
            self.pwd_js = f.read().decode()
        with open('./js/slider.js', 'rb') as f:
            self.slider_js = f.read().decode()
        with open('./js/token.js', 'rb') as f:
            self.token_js = f.read().decode()

        # 密码错误重置初始化
        self.reset_flag = False

    @staticmethod
    def check_islogin(cookies):
        """
        检查是否登录成功
        :return:
        """
        url = 'https://www.meituan.com/ptapi/getLoginedUserInfo'
        result = requests.get(url, cookies=cookies, headers={
            'Referer': 'https://www.meituan.com/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
        }).json()
        if 'nickName' in set(result.keys()):
            return True
        return False

    @staticmethod
    def _get_fingerprint():
        # 进入浏览器设置
        options = Options()
        # 设置中文
        options.add_argument('lang=zh_CN.UTF-8')
        options.add_argument('--headless')
        options.add_argument(
            'user-agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36"'
        )
        browser = webdriver.Chrome(options=options)

        browser.get('file:///D:/Meituan/fingerprint.html')
        time.sleep(2)
        html = browser.page_source
        fingerprint = re.search('</script>(.*?)</body>', html).group(1)
        browser.quit()
        return fingerprint

    def _get_token(self, url):
        ctx = execjs.compile(self.token_js)
        return ctx.call('get_token', url)

    def _get_behavior_token(self, page_data):
        ctx = execjs.compile(self.slider_js)
        verify_data = ctx.call('get_behavior_token', page_data)
        return verify_data

    def _encrypt_pwd(self):
        """
        RSA加密密码
        :return:
        """
        ctx = execjs.compile(self.pwd_js)
        pwd = ctx.call('encrypt', self.password)
        return pwd

    def _init_slider(self, requests_code):
        """
        初始化滑块
        :param requests_code:
        :return:
        """
        data = {
            'requestCode': requests_code,
            'feVersion': '1.4.0',
            'source': '1'
        }
        url = 'https://verify.meituan.com/v2/ext_api/page_data'
        result = self.session.post(url, data=data).json()
        if result['status']:
            return result['data']
        return None

    def _slider_verify(self, code, request_code):
        """
        滑块风控验证
        :param code:
        :param request_code:
        :return:
        """
        page_data = None
        for _ in range(5):
            page_data = self._init_slider(request_code)
            if page_data:
                break
        if not page_data:
            raise Exception('滑块初始化失败! ')

        url = 'https://verify.meituan.com/v2/ext_api/merchantlogin/verify?id=71'

        verify_data = self._get_behavior_token(page_data)
        self.session.headers.update({
            'Authorization': 'Bearer ' + request_code,
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': 'https://epassport.meituan.com',
        })
        data = {
            'request_code': request_code,
            'behavior': verify_data['behavior'],
            'fingerprint': '',
            '_token': verify_data['token'],
        }
        result = self.session.post(url, data=data).json()
        if result['status']:
            self.logger.info('成功通过滑块验证!')
            if code == 101157:
                return code
            elif code == 101190:
                return result['data']['response_code']
            else:
                print(result)
                raise Exception('未知类型请求! ')
        raise Exception('滑块验证失败! ')

    def _init_captcha(self, request_code):
        url = 'https://verify.meituan.com/v2/captcha?'
        params = {
            'request_code': request_code,
            'action': 'login',
            'randomId': '0.6868395303586443',
            '_token': self._get_token(url)
        }
        resp = self.session.get(url, params=params)
        with open('captcha.png', 'wb') as f:
            f.write(resp.content)

        img = Image.open('captcha.png')
        img.show()
        verify_code = input('验证码  >> \n')

        return verify_code

    def _captcha_verify(self, code, verify_code):
        """
        图文识别验证码
        :param code:
        :param verify_code:
        :return:
        """
        url = 'https://verify.meituan.com/v2/ext_api/login/verify?id=1'

        data = {
            'id': '71',
            'request_code': code,
            'captchacode': verify_code,
            '_token': self._get_token(url)
        }

        resp = self.session.post(url, data=data).json()
        if resp['status'] == 1:
            return resp['data']['response_code']
        return None

    def _init_smscode(self, request_code):
        """
        请求手机验证码接口
        :return:
        """
        url = 'https://verify.meituan.com/v2/ext_api/loginverification/info?id=4'
        data = {
            'request_code': request_code,
            'mobile': '',
            'moduleEnable': 'true',
            'listIndex': 0,
            '_token': self._get_token(url)
        }
        resp = self.session.post(url, data=data).json()
        if resp['status'] == 0:
            msg = resp['error']['message']
            self.logger.warning(msg)
            code = resp['error']['code']
            print(code)
            request_code = resp['error']['request_code']
            success = self._slider_verify(code, request_code)
            if success:
                self.logger.info('成功通过滑块验证! ')
                return True
            return False
        elif resp['status'] == 1:
            return True
        return False

    def _smscode_verify(self, request_code):
        """
        发送手机验证码
        :return:
        """
        success = False
        for _ in range(5):
            success = self._init_smscode(request_code)
            if success:
                break
        if not success:
            raise Exception('手机验证码接口请求失败! ')

        url = 'https://verify.meituan.com/v2/ext_api/loginverification/verify?id=4'
        time.sleep(30)
        sms_code = input('请输入手机验证码  >> \n')
        data = {
            'mobile': '',
            'request_code': request_code,
            'smscode': sms_code,
            'listIndex': 0,
            '_token': self._get_token(url)
        }
        resp = self.session.post(url, data=data).json()
        if resp['status'] == 1:
            self.logger.info('成功通过手机验证! ')
            return resp['data']['response_code']
        raise Exception('手机验证失败! ')

    def _get_csrf(self):
        """
        获取认证Csrf参数
        :return:
        """
        url = 'https://passport.meituan.com/account/unitivelogin?service=www&continue=https%3A%2F%2Fwww.meituan.com%2Faccount%2Fsettoken%3Fcontinue%3Dhttp%253A%252F%252Fcd.meituan.com%252F'

        resp = self.session.get(url)
        soup = BeautifulSoup(resp.text, 'lxml')
        csrf = soup.select('input[name="csrf"]')[0]['value']

        return csrf

    def login(self, csrf, request_code='', response_code=''):
        """
        模拟登录
        :return:
        """
        login_api = 'https://passport.meituan.com/account/unitivelogin?risk_partner=0&risk_platform=1&risk_app=-1&uuid=ea8b149299ce4622b486.1568870998.1.0.0&service=www&continue=https%3A%2F%2Fwww.meituan.com%2Faccount%2Fsettoken%3Fcontinue%3Dhttps%253A%252F%252Fhf.meituan.com%252F'

        pwd = self._encrypt_pwd()

        self.session.headers.update({
            'Referer': 'https://passport.meituan.com/account/unitivelogin?service=www&continue=https%3A%2F%2Fwww.meituan.com%2Faccount%2Fsettoken%3Fcontinue%3Dhttp%253A%252F%252Fcd.meituan.com%252F',
            'X-CSRF-Token': csrf,
            'X-Client': 'javascript',
            'X-Requested-With': 'XMLHttpRequest',
        })
        if 'Authorization' in set(self.session.headers):
            del self.session.headers['Authorization']
        data = {
            'countrycode': '86',
            'email': self.username,
            'password': pwd,
            'origin': 'account-login',
            'csrf': csrf,
            'requestCode': request_code,
            'responseCode': response_code,
            'h5Fingerprint': ''
        }
        result = self.session.post(login_api, data=data).json()

        return result

    @loopUnlessSeccessOrMaxTry(3, sleep_time=0.5)
    def login_process(self):
        """
        整体登录流程
        :return:
        """
        csrf = self._get_csrf()
        result = self.login(csrf)
        if 'data' in set(result.keys()):
            self.logger.info('登录成功! ')
            # token = result['data']['token']
            nickname = result['data']['userName']
            self.logger.info('Hello, {}! '.format(nickname))
            cookies = self.session.cookies.get_dict()
            if self.check_islogin(cookies):
                self.logger.info('Cookies 有效! ')
                self.redis_client.save_cookies(self.site, self.username, cookies)
                return True
            else:
                raise Exception('登录失败! ')
        else:
            if result['error']['code'] == 101190:
                msg = result['error']['message']
                self.logger.warning(msg)
                code = result['error']['code']
                request_code = result['error']['data']['requestCode']
                response_code = self._slider_verify(code, request_code)
                result = self.login(csrf, request_code, response_code)
                if result['success']:
                    self.logger.info('登录成功! ')
                    nickname = result['data']['userName']
                    self.logger.info('Hello, {}! '.format(nickname))
                    cookies = self.session.cookies.get_dict()
                    if self.check_islogin(cookies):
                        self.logger.info('Cookies 有效! ')
                        self.redis_client.save_cookies(self.site, self.username, cookies)
                        return True
                    else:
                        raise Exception('登录失败! ')
                else:
                    if result['error']['code'] == 101157:
                        msg = result['error']['message'].replace('验证', '手机验证')
                        self.logger.warning(msg)
                        request_code = result['error']['data']['param'].split('&')[1].split('=')[1]
                        response_code = self._smscode_verify(request_code)
                        result = self.login(request_code, response_code)
                        if result.get('data', 0):
                            self.logger.info('登录成功! ')
                            nickname = result['data']['userName']
                            self.logger.info('Hello, {}! '.format(nickname))
                            cookies = self.session.cookies.get_dict()
                            if self.check_islogin(cookies):
                                self.logger.info('Cookies 有效! ')
                                self.redis_client.save_cookies(self.site, self.username, cookies)
                                return True
                            else:
                                raise Exception('Cookies 失效! ')
                        else:
                            raise Exception('登录失败! ')
                    elif result['error']['code'] == 101135:
                        msg = result['error']['message']
                        self.logger.warning(msg)
                        return False
                    else:
                        raise Exception('登录失败: ', result['error']['message'])
            elif result['error']['code'] == 101157:
                msg = result['error']['message'].replace('验证', '手机验证')
                self.logger.warning(msg)
                request_code = result['error']['data']['param'].split('&')[1].split('=')[1]
                response_code = self._smscode_verify(request_code)
                result = self.login(request_code, response_code)
                if result.get('data', 0):
                    self.logger.info('登录成功! ')
                    nickname = result['data']['userName']
                    self.logger.info('Hello, {}! '.format(nickname))
                    cookies = self.session.cookies.get_dict()
                    if self.check_islogin(cookies):
                        self.logger.info('Cookies 有效! ')
                        self.redis_client.save_cookies(self.site, self.username, cookies)
                        return True
                    else:
                        raise Exception('Cookies 失效! ')
                else:
                    raise Exception('登录失败! ')
            elif result['error']['code'] == 101135:
                msg = result['error']['message']
                self.logger.warning(msg)
                return False
            else:
                raise Exception('登录失败: ', result['error']['message'])

    @check_user()
    def run(self, load_cookies: bool = True):

        if load_cookies:
            cookies = self.redis_client.load_cookies(self.site, self.username)
            if cookies:
                if self.check_islogin(cookies):
                    return True
                self.logger.warning('Cookies 已过期')

        self.login_process()


if __name__ == '__main__':
    MeituanLogin('16533101673', 'xuzhihai0723').run(load_cookies=False)
