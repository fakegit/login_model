# -*- coding: utf-8 -*-
# @Time    : 2019/8/3 12:10
# @Author  : Esbiya
# @Email   : 18829040039@163.com
# @File    : baidu_login.py
# @Software: PyCharm

import re
from PIL import Image
from urllib.request import urlretrieve
import requests
from base64 import b64encode
from utils import *
from cookies_pool import RedisClient
from chaojiying import image_to_text
from uuid import uuid4
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5 as Cipher_pkcs1_v1_5


class BaiduLogin:

    def __init__(self, username: str = None, password: str = None):
        self.site = 'baidu'
        self.username = username
        self.password = password
        self.logger = get_logger()
        self.redis_client = RedisClient(self.logger)
        self.session = requests.session()
        self.session.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_1) AppleWebKit/601.2.7 (KHTML, like Gecko) Version/9.0.1 Safari/601.2.7',
            'Referer': 'https://pan.baidu.com/',
        }

        # 密码错误重置初始化
        self.reset_flag = False

    def check_islogin(self, cookies):
        """
        ...
        :param cookies:
        :return:
        """
        pass

    def _init_cookies(self):
        """
        访问百度网盘首页初始化 cookies
        :return:
        """
        self.session.get('https://pan.baidu.com/')

    @staticmethod
    def _get_gid():
        return str(uuid4()).upper()

    def _get_token(self, gid):
        """
        获取登录 token 认证
        :return:
        """
        url = 'https://passport.baidu.com/v2/api/?getapi'
        params = {
            'getapi': '',
            'tpl': 'mn',
            'apiver': 'v3',
            'tt': str(int(time.time() * 1000)),
            'class': 'login',
            'gid': gid,
            'loginversion': 'v4',
            'logintype': 'dialogLogin',
            'traceid': '',
            'callback': 'bd__cbs__pivyke',
        }
        resp = self.session.get(url=url, params=params)
        js = parse_json(resp.text.replace("\'", "\""))
        return js['data']['token']

    def _get_public_key(self, gid, token):
        """
        获取 RSA 加密公钥
        :return:
        """
        url = 'https://passport.baidu.com/v2/getpublickey'
        params = {
            'token': token,
            'tpl': 'mn',
            'apiver': 'v3',
            'tt': str(int(time.time() * 1000)),
            'gid': gid,
            'loginversion': 'v4',
            'traceid': '',
            'callback': 'bd__cbs__h02h0j'
        }
        resp = self.session.get(url=url, params=params)
        js = parse_json(resp.text.replace("\'", "\""))
        key, public_key = js.get('key'), js.get('pubkey')
        return key, public_key

    def _encrypt_pwd(self, public_key):
        rsa_key = RSA.importKey(public_key)
        encryptor = Cipher_pkcs1_v1_5.new(rsa_key)
        cipher = b64encode(encryptor.encrypt(self.password.encode('utf-8')))
        return cipher.decode('utf-8')

    def _get_verifycode(self, code_string):
        """
        使用超级鹰识别验证码
        :param pcid:
        :return:
        """
        captcha_url = f'https://passport.baidu.com/cgi-bin/genimage?{code_string}'
        img_data = self.session.get(captcha_url).content
        self.logger.info('使用超级鹰识别验证码...')
        ok, result = image_to_text(img_data)
        if ok:
            self.logger.info('成功识别验证码！')
            return result
        raise Exception('验证码识别失败: ', result)

    def _verify_phone(self, authtoken, lstr, ltoken, loginproxy):
        """
        手机验证
        :return:
        """
        url = 'https://passport.baidu.com/v2/sapi/authwidgetverify?'
        params = {
            "authtoken": authtoken,
            "type": "mobile",
            "jsonp": "1",
            "apiver": "v3",
            "verifychannel": "",
            "action": "getapi",
            "vcode": "",
            "questionAndAnswer": "",
            "needsid": "",
            "rsakey": "",
            "countrycode": "",
            "subpro": "",
            "u": "https://www.baidu.com/",
            "lstr": lstr,
            "ltoken": ltoken,
            "tpl": "mn",
            "winsdk": "",
            "authAction": "",
            "traceid": "00BC1501",
            "callback": "bd__cbs__h3w9ui"
        }

        res = self.session.get(url, params=params)
        encode_str = res.text.replace('bd__cbs__h3w9ui(', '').replace(')', '').replace('{', '').replace('}', '').replace('"', '').replace("'", '').replace(' ', '')
        result = {item.split(':')[0]: item.split(':')[1] for item in encode_str.split(',')}
        if result['errno'] == '110000':
            self.logger.info('成功请求验证码接口! ')
            params.update({
                "action": "send",
            })
            resp = self.session.get(url, params=params)
            encode_str = resp.text.replace('bd__cbs__h3w9ui(', '').replace(')', '').replace('{', '').replace(
                '}', '').replace('"', '').replace("'", '').replace(' ', '')
            result = {item.split(':')[0]: item.split(':')[1] for item in encode_str.split(',')}
            if result['errno'] == '110000':
                self.logger.info('验证码发生中, 请注意接收...')
                time.sleep(1)
                verify_code = input('请输入验证码 >> \n')
                params.update({
                    "action": "check",
                    "vcode": verify_code,
                })
                respo = self.session.get(url, params=params)
                encode_str = respo.text.replace('bd__cbs__h3w9ui(', '').replace(')', '').replace('{', '').replace(
                    '}', '').replace('"', '').replace("'", '').replace(' ', '')
                result = {item.split(':')[0]: item.split(':')[1] for item in encode_str.split(',')}
                if result['errno'] == '110000':
                    self.logger.info('手机验证成功! ')
                    response = self.session.get(loginproxy)
                    print(response.text)
                    return True
        elif result['errno'] == '110002':
            self.logger.error(result['msg'])
            return False

    @loopUnlessSeccessOrMaxTry(3, sleep_time=3)
    def login(self):

        self._init_cookies()
        gid = self._get_gid()
        token = self._get_token(gid)
        key, public_key = self._get_public_key(gid, token)
        pwd = self._encrypt_pwd(public_key)

        login_api = 'https://passport.baidu.com/v2/api/?login'
        data = {
            'staticpage': 'https://www.baidu.com/cache/user/html/v3Jump.html',
            'charset': 'UTF-8',
            'token': token,
            'tpl': 'netdisk',
            'subpro': 'netdisk_web',
            'apiver': 'v3',
            'tt': str(int(time.time() * 1000)),
            'codestring': '',
            'safeflg': '0',
            'u': 'https://www.baidu.com/',
            'isPhone': 'false',
            'detect': '1',
            'gid': gid,
            'quick_user': '0',
            'logintype': 'dialogLogin',
            'logLoginType': 'pc_loginDialog',
            'idc': '',
            'loginmerge': 'true',
            'splogin': 'rate',
            'username': self.username,
            'password': pwd,
            'rsakey': key,
            'crypttype': '12',
            'ppui_logintime': 389548,
            'countrycode': '',
            'loginversion': 'v4',
            'traceid': '',
            'callback': 'parent.bd__pcbs__oxzeyj'
        }
        for _ in range(10):
            resp = self.session.post(login_api, data=data)

            result_str = re.search(r'.*href \+= "(.*)"\+accounts', resp.text).group(1)
            result = {x.split('=')[0]: x.split('=')[1] for x in result_str.split('&')}

            if result['err_no'] == '0':
                self.logger.info('登录成功! ')
                cookies = resp.cookies.get_dict()
                self.redis_client.save_cookies(self.site, self.username, cookies)
                return cookies
            elif result['err_no'] in {'6', '257'}:
                code_str = result.get('codeString')
                self.logger.warning('请输入验证码! ')
                verify_code = self._get_verifycode(code_str)
                data.update({'codestring': code_str, 'verifycode': verify_code})
            elif result['err_no'] == '120021':
                self.logger.warning('账号存在风险, 请进行手机验证! ')
                authtoken = result['authtoken']
                lstr = result['lstr']
                ltoken = result['ltoken']
                loginproxy = result['loginproxy']
                flag = self._verify_phone(authtoken, lstr, ltoken, loginproxy)
                if not flag:
                    return None
            elif result['err_no'] in {'4', '7'}:
                self.reset_flag = True
                raise Exception('账号或密码错误! ')
            return None

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
    x = BaiduLogin().run()
    print(x)
