# -*- coding: utf-8 -*-
# @Time    : 2019/8/5 20:51
# @Author  : xuzhihai0723
# @Email   : 18829040039@163.com
# @File    : renren_login.py
# @Software: PyCharm


import requests
import execjs
from bs4 import BeautifulSoup
from urllib.parse import urlencode
from utils import *
from chaojiying import image_to_text
from cookies_pool import RedisClient


class RenrenLogin:

    def __init__(self, username: str = None, password: str = None):
        self.site = 'renren'
        self.logger = get_logger()
        self.username = username
        self.password = password
        self.redis_client = RedisClient(self.logger)
        self.session = requests.session()
        self.session.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.80 Safari/537.36'
        }
        with open('encryptPwd.js', 'rb') as f:
            js = f.read().decode()

        self.ctx = execjs.compile(js)

        # 密码错误重置初始化
        self.reset_flag = False

    def check_islogin(self, cookies):
        """
        检查是否登录成功
        :return:
        """
        res = self.session.get('http://www.renren.com/home', cookies=cookies)
        if 'hd-name' in res.text:
            bsobj = BeautifulSoup(res.text, 'lxml')
            nickname = bsobj.select('.hd-name')[0].get_text()
            self.logger.info('Cookies 有效! ')
            self.logger.info(f'Hello, {nickname}! ')
            return True
        return False

    def _init_cookies(self):
        """
        访问首页初始化 Cookie
        :return:
        """
        self.session.get('http://www.renren.com/')

    def _get_rkey(self):
        """
        获取加密所需密钥和 rkey 参数
        :return:
        """
        url = 'http://login.renren.com/ajax/getEncryptKey'
        res = self.session.get(url).json()

        if res['isEncrypt']:
            iv = res['e']
            encryptKey = res['n']
            rkey = res['rkey']
            return iv, encryptKey, rkey
        raise Exception('获取密钥出错! ')

    def _encrypt_pwd(self, iv, encryptKey):
        return self.ctx.call('encrypt', self.password, iv, encryptKey)

    def _get_uniquetimestamp(self):
        return self.ctx.call('getUniqueTimestamp')

    def _show_captcha(self):
        """
        访问接口判断是否需要验证码
        :return:
        """
        url = 'http://www.renren.com/ajax/ShowCaptcha'
        data = {
            'email': self.username,
            '_rtk': 'a0cdef52'
        }
        res = self.session.post(url, data=data)
        if '0' in res.text:
            self.logger.info('此次登录无需验证码! ')
            return False
        return True

    def _get_verifycode(self):
        captcha_url = 'http://icode.renren.com/getcode.do?t=web_login&rnd=0.28838133194471105'
        img_data = self.session.get(captcha_url).content
        self.logger.info('使用超级鹰识别验证码...')
        ok, result = image_to_text(img_data)
        if ok:
            self.logger.info('成功识别验证码！')
            return result
        raise Exception('验证码识别失败: ', result)

    @loopUnlessSeccessOrMaxTry(3, sleep_time=3)
    def login(self):

        params = {
            '1': 1,
            'uniqueTimestamp': self._get_uniquetimestamp()
        }

        login_api = 'http://www.renren.com/ajaxLogin/login?' + urlencode(params)

        self._init_cookies()
        iv, encryptKey, rkey = self._get_rkey()
        pwd = self._encrypt_pwd(iv, encryptKey)

        flag = self._show_captcha()
        if flag:
            icode = self._get_verifycode()
        else:
            icode = ''
        data = {
            'email': self.username,
            'icode': icode,
            'origURL': 'http://www.renren.com/home',
            'domain': 'renren.com',
            'key_id': '1',
            'captcha_type': 'web_login',
            'password': pwd,
            'rkey': rkey,
            'f': 'http%3A%2F%2Fwww.renren.com%2F971788971'
        }
        self.session.headers['Referer'] = 'http://www.renren.com/SysHome.do'
        res = self.session.post(login_api, data=data)

        if 'failCode' not in res.text:
            self.logger.info('登录成功! ')

            resp = self.session.get('http://www.renren.com/home', allow_redirects=False)
            redirect_url = resp.headers['location']

            cookies = self.session.cookies.get_dict()

            # 巨坑... 这里返回的 cookies 中的 t 的值需要替换为 societyguester 的值
            # 真正起作用的 cookie 就是 t这个键 和 societyguester 的值, 其他 cookie 可以不要。
            cookies['t'] = cookies['societyguester']
            self.redis_client.save_cookies(self.site, self.username, cookies)

            response = self.session.get(redirect_url)
            bsobj = BeautifulSoup(response.text, 'lxml')
            nickname = bsobj.select('.hd-name')[0].get_text()
            self.logger.info('Hello, {}! '.format(nickname))
            return True
        elif res.json()['failCode'] == 128:
            self.reset_flag = True
            raise Exception('账号或密码错误! ')
        elif res.json()['failCode'] == 512:
            raise Exception(res.json()['failDescription'])
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
    RenrenLogin().run(load_cookies=False)
