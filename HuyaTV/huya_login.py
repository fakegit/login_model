# -*- coding: utf-8 -*-
# @Time    : 2019/7/25 22:11
# @Author  : Esbiya
# @Email   : 18829040039@163.com
# @File    : demo.py
# @Software: PyCharm

import re
import json
import execjs
import requests
from utils import *
from bs4 import BeautifulSoup
from cookies_pool import RedisClient


class HuyaLogin:

    def __init__(self, username: str = None, password: str = None):
        self.site = 'huya'
        self.logger = get_logger()
        self.username = username
        self.password = password
        self.redis_client = RedisClient(self.logger)
        self.session = requests.session()
        self.session.headers = {
            'content-type': 'application/json;charset=UTF-8',
            'lcid': '2052',
            'uri': '30001',
            'Origin': 'https://udblgn.huya.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.80 Safari/537.36'
        }
        # 密码错误重置初始化
        self.reset_flag = False

    def check_islogin(self, cookies):
        """
        检查登录, 请求用户主页若出现用户名则登录成功
        :return:
        """
        res = self.session.get('https://i.huya.com/', cookies=cookies)
        bsobj = BeautifulSoup(res.text, 'lxml')
        if bsobj.find('h2', {'class': 'uesr_n'}):
            nickname = bsobj.find('h2', {'class': 'uesr_n'}).get_text()
            self.logger.info('登录成功! ')
            self.logger.info('Hello, {}! '.format(nickname))
            self.redis_client.save_cookies(self.site, self.username, cookies)
            return True
        return False

    def _get_sdid(self):
        url = 'https://udblgn.huya.com/web/middle/2.3/37893475/https/787b6ffa5e4c42a99091ab91d071ed2a'
        resp = self.session.get(url)
        sdid = re.search(r'HyUDBWebSDK_Exchange.init\((.*?)\);', resp.text).group(1)
        return sdid

    def encrypt(self):
        with open('encrypt.js', 'rb') as f:
            js = f.read().decode()

        ctx = execjs.compile(js)

        password = ctx.call('encryptPwd', self.password)
        request_id = ctx.call('getRequestId', 1)
        page = ctx.call('getPage', 'https://www.huya.com/l')
        # 页面cookie, 没有测试过期时间
        context = ctx.call('getContext', '__yamid_tt1=0.1232795775887836; __yamid_new=C875D5606C80000176AD12EEAE0014D2; SoundValue=0.50; alphaValue=0.80; guid=3ad7b83861a9ea5c33512be62ce6b2fa; Hm_lvt_51700b6c722f5bb4cf39906a596ea41f=1558882650,1559909095,1559998946; __yasmid=0.1232795775887836; udb_passdata=3; isInLiveRoom=true; udb_guiddata=787b6ffa5e4c42a99091ab91d071ed2a; web_qrlogin_confirm_id=bf407b38-0a04-453a-8899-c93acf12f406; h_unt=1560003929; Hm_lpvt_51700b6c722f5bb4cf39906a596ea41f=1560003939; __yaoldyyuid=; _yasids=__rootsid%3DC87A02DEAC400001CC501DC016A81329; PHPSESSID=qdd0udkruqk8mi2u0unr4p53r5')
        return password, request_id, page, context

    @loopUnlessSeccessOrMaxTry(3, sleep_time=3)
    def login(self):
        sdid = self._get_sdid()
        password, request_id, page, context = self.encrypt()
        self.session.headers.update({
            'context': context,
            'reqid': str(request_id),
            'Referer': 'https://udblgn.huya.com/web/middle/2.3/854732/https/{}'.format(context.split('-')[1])
        })
        payload = {
            'appId': "5002",
            'byPass': "3",
            'context': context,
            'data': {
                'userName': "17570759427",
                'password': password,
                'domainList': "",
                'behavior': "%5B%7B%22page.login%22%3A%220.073%22%7D%2C%7B%22input.l.account%22%3A%222.856%22%7D%2C%7B%22input.l.passwd%22%3A%225.37%22%7D%2C%7B%22button.UDBSdkLogin%22%3A%228.387%2C138%2C254%22%7D%5D",
                'page': page,
                'randomStr': "",
                'remember': "1"
            },
            'lcid': "2052",
            'requestId': str(request_id),
            'sdid': str(sdid),
            'smid': "",
            'uri': "30001",
            'version': "2.4"
        }
        url = 'https://udblgn.huya.com/web/v2/passwordLogin'
        res = self.session.post(url, data=json.dumps(payload))
        cookies = res.cookies.get_dict()
        if self.check_islogin(cookies):
            return cookies
        elif res.json()['description'] == '账号或密码错误':
            self.reset_flag = True
            raise Exception('账号或密码错误! ')
        raise Exception('登录失败: {}'.format(res.json()['description']))

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
    x = HuyaLogin().run(load_cookies=False)
    print(x)
