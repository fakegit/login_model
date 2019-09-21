# -*- coding: utf-8 -*-
# @Time    : 2019/7/21 9:35
# @Author  : Esbiya
# @Email   : 18829040039@163.com
# @File    : weibo_login.py
# @Software: PyCharm

import requests
import re
import chardet
import execjs
from chaojiying import image_to_text
from utils import *
from bs4 import BeautifulSoup
from cookies_pool import RedisClient


class WeiboLogin:

    def __init__(self, username: str = None, password: str = None):
        self.site = 'weibo'
        self.logger = get_logger()
        self.redis_client = RedisClient(self.logger)
        self.username = username
        self.password = password
        self.session = requests.session()
        self.session.headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Referer': 'https://weibo.com/',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.75 Mobile Safari/537.36'
        }
        # 密码错误重置初始化
        self.reset_flag = False

    def check_islogin(self, cookies):
        """
        检查是否登录成功
        :return:
        """
        res = self.session.get('http://my.sina.com.cn/', cookies=cookies)
        html = res.content.decode(chardet.detect(res.content)['encoding'])
        bsobj = BeautifulSoup(html, 'lxml')
        if bsobj.find('p', {'class': 'me_name'}):
            nickname = bsobj.find('p', {'class': 'me_name'}).get_text()
            self.logger.info('Cookies 有效! ')
            self.logger.info(f'Hello, {nickname}! ')
            return True
        elif '立即登录' in res.text:
            return False
        return False

    @staticmethod
    def _load_js(jsfilename):
        """
        打开js脚本并加载
        :return:
        """
        with open(jsfilename, 'r') as f:
            js = f.read()
        ctx = execjs.compile(js)
        return ctx

    def _get_su(self, ctx):
        """
        获取su参数
        :return:
        """
        su = ctx.call('getSu', self.username)
        return su

    def _get_params(self, su):
        """
        获取pcid, nonce, pubkey, servertime, rsakv
        :param su:
        :return:
        """
        url = 'https://login.sina.com.cn/sso/prelogin.php?'
        params = {
            'entry': 'weibo',
            'callback': 'sinaSSOController.preloginCallBack',
            'su': su,
            'rsakt': 'mod',
            'checkpin': '1',
            'client': 'ssologin.js(v1.4.19)',
            '_': int(time.time() * 1000)
        }

        res = self.session.get(url, params=params).text
        result = json.loads(re.search(r'sinaSSOController.preloginCallBack\((.*?)\)', res).group(1))
        pcid = result['pcid']
        nonce = result['nonce']
        pubkey = result['pubkey']
        servertime = result['servertime']
        rsakv = result['rsakv']
        return pcid, nonce, pubkey, servertime, rsakv

    def _get_verifycode(self, pcid):
        captcha_url = f'https://login.sina.com.cn/cgi/pin.php?r=16343619&s=0&p={pcid}'
        img_data = self.session.get(captcha_url).content
        self.logger.info('使用超级鹰识别验证码...')
        ok, result = image_to_text(img_data)
        if ok:
            self.logger.info('成功识别验证码！')
            return result
        raise Exception('验证码识别失败: ', result)

    def _get_sp(self, ctx, pubkey, servertime, nonce):
        """
        获取sp参数
        :param ctx:
        :return:
        """
        sp = ctx.call('getSp', pubkey, servertime, nonce, self.password)
        return sp

    @loopUnlessSeccessOrMaxTry(3, sleep_time=3)
    def login(self):
        """
        登录
        :return:
        """
        login_api = f'https://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.19)&_={int(time.time()*1000)}'

        ctx = self._load_js('encryptUN.js')
        su = self._get_su(ctx)
        pcid, nonce, pubkey, servertime, rsakv = self._get_params(su)
        verify_code = self._get_verifycode(pcid)
        ctx_ = self._load_js('encryptPW.js')
        sp = self._get_sp(ctx_, pubkey, servertime, nonce)

        data = {
            'entry': 'weibo',
            'gateway': '1',
            'from': '',
            'savestate': '7',
            'qrcode_flag': 'false',
            'useticket': '1',
            'pagerefer': 'https://login.sina.com.cn/crossdomain2.php?action=logout&r=https%3A%2F%2Fpassport.weibo.com%2Fwbsso%2Flogout%3Fr%3Dhttps%253A%252F%252Fweibo.com%26returntype%3D1',
            'pcid': pcid,
            'door': verify_code,
            'vsnf': '1',
            'su': su,
            'service': 'miniblog',
            'servertime': servertime,
            'nonce': nonce,
            'pwencode': 'rsa2',
            'rsakv': rsakv,
            'sp': sp,
            'sr': '1440*561',         # 屏幕大小
            'encoding': 'UTF-8',
            'cdult': '2',
            'domain': 'weibo.com',
            'prelt': '48',
            'returntype': 'TEXT'
        }
        res = self.session.post(login_api, data=data)
        cookies = res.cookies.get_dict()
        if self.check_islogin(cookies):
            self.redis_client.save_cookies(self.site, self.username, cookies)
            return cookies
        elif res.json()['reason'] == '登录名或密码错误' or res.json()['reason'] == '请输入正确的密码':
            self.reset_flag = True
            raise Exception('账号或密码错误! ')
        raise Exception(res.json()['reason'])

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
                    return cookies
                self.logger.warning('Cookies 已过期! ')

        return self.login()


if __name__ == '__main__':
    x = WeiboLogin().run(load_cookies=False)
    print(x)
