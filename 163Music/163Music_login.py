# -*- coding: utf-8 -*-
# @Time    : 2019/7/28 11:27
# @Author  : Esbiya
# @Email   : 18829040039@163.com
# @File    : redies_db.py
# @Software: PyCharm

import requests
import codecs
import base64
import random
import math
import demjson
import hashlib
from utils import *
import re
import os
import execjs
from selenium import webdriver
from Crypto.Cipher import AES
from cookies_pool import RedisClient


class WangyiyunLogin:

    def __init__(self, username: str = None, password: str = None):
        self.site = 'wangyiyun'
        self.username = username
        self.password = password
        self.logger = get_logger()
        self.redis_client = RedisClient(self.logger)

        # 密码错误重置初始化
        self.reset_flag = False

    def check_islogin(self, cookies):
        res = requests.get('https://music.163.com/#/user/home?', cookies=cookies)
        # 注: 正则拿到的 json 字符串中 key 没有被括起来(json 默认字典里的字符串为双引号括起来), 转 json 会报错, demjson 库可以修改 json 格式错误
        json_str = re.search('var GUser=(.*?);', res.text, re.S).group(1)
        user_info = demjson.decode(json_str)
        if user_info:
            self.logger.info('登录成功! ')
            self.logger.info('Hello, {}! '.format(user_info['nickname']))
            return True
        return False

    def get_wm_did(self):
        """
        获取 WM_DID
        :return:
        """
        options = webdriver.ChromeOptions()
        # 设置为开发者模式，避免被识别, 开发者模式下 webdriver 属性为 undefined
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        options.add_argument('--headless')
        browser = webdriver.Chrome(options=options)

        browser.get("https://music.163.com/#/login")
        time.sleep(1)
        WM_DID = browser.execute_script('return window.localStorage["WM_DID"]')
        param = WM_DID.split('__')[0]
        stime = WM_DID.split('__')[2][:10]
        etime = WM_DID.split('__')[1][:10]
        start_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(WM_DID.split('__')[2][:10])))
        end_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(WM_DID.split('__')[1][:10])))
        self.logger.info('{} 有效时间: {} - {}'.format(param, start_time, end_time))
        browser.close()

        with open('param.txt', 'w') as f:
            f.write(param + '\n')
            f.write(stime + '\n')
            f.write(etime)

        return param

    def get_checktoken(self):
        """
        获取 token 认证
        :return:
        """
        with open('param.txt', 'r') as f:
            lines = f.readlines()
        param = lines[0].replace('\n', '')
        stime = int(lines[1].replace('\n', ''))
        etime = int(lines[2])
        current_time = int(time.time())
        if stime < current_time < etime:
           self.logger.info('{} 有效! '.format(param))
        else:
            self.logger.warning('{} 已过期, 等待访问首页重新获取! '.format(param))
            param = self.get_wm_did()
        with open('get_checktoken.js', 'rb') as f:
            js = f.read().decode()
        ctx = execjs.compile(js)
        return ctx.call('getCheckToken', param)

    def md5_encrypt(self):
        """
        md5加密密码
        :return:
        """
        md5 = hashlib.md5()
        md5.update(self.password.encode())
        encrypt_pwd = md5.hexdigest()
        return encrypt_pwd

    @staticmethod
    def get_random_str():
        """
        获取一个随机16位字符串
        :return: 随机16位字符串
        """
        str = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        res = ''
        for x in range(16):
            index = math.floor(random.random() * len(str))
            res += str[index]
        return res

    @staticmethod
    def aes_encrypt(text, key):
        """
        AES加密
        :param text: 待加密密文
        :param key: 密钥
        :return:
        """
        # iv: 偏移量
        iv = b'0102030405060708'
        # 注：AES只能加密数字和字母，无法加密中文。
        # 解决方法：在CBC加密模式下，字符串必须补齐长度为16的倍数，且长度指标不能为中文，需转化为unicode编码长度
        pad = 16 - len(text.encode()) % 16
        text = text + pad * chr(pad)
        encryptor = AES.new(key.encode('utf-8'), AES.MODE_CBC, iv)
        # 最后还需要进行base64加密
        msg = base64.b64encode(encryptor.encrypt(text.encode('utf-8')))
        return msg

    @staticmethod
    def rsa_encrypt(value, text, modulus):
        """
        RSA加密
        :param value: 加密指数
        :param text: 待加密密文
        :param modulus: 加密系数
        :return:
        """
        text = text[::-1]
        rs = int(codecs.encode(text.encode('utf-8'), 'hex_codec'), 16) ** int(value, 16) % int(modulus, 16)
        return format(rs, 'x').zfill(256)

    def get_data(self):
        """
        params：进行了两次AES加密
        encSecKey：进行了一次RSA加密
        :return:
        """
        encrypt_pwd = self.md5_encrypt()
        checkToken = self.get_checktoken()
        data = {
            "phone": self.username,
            "password": encrypt_pwd,
            "rememberLogin": "true",
            "checkToken": checkToken,
            "csrf_token": ""
        }
        text = json.dumps(data)
        random_text = self.get_random_str()

        # params: 两次AES加密
        params = self.aes_encrypt(text, '0CoJUm6Qyw8W8jud')
        params = self.aes_encrypt(params.decode('utf-8'), random_text).decode('utf-8')

        # RSA加密系数, 固定值
        module = "00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5a" \
                 "a76d2e417629ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46be" \
                 "e255932575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7"
        # encSeckey: 一次 RSA 加密, '010001' 为加密指数, 固定值
        encSecKey = self.rsa_encrypt('010001', random_text, module)
        return {
            'params': params,
            'encSecKey': encSecKey
        }

    @loopUnlessSeccessOrMaxTry(3, sleep_time=3)
    def login(self):
        login_api = 'https://music.163.com/weapi/login/cellphone?csrf_token='
        data = self.get_data()
        headers = {
            'referer': 'https://music.163.com/',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.80 Safari/537.36'
        }
        res = requests.post(login_api, data=data, headers=headers)
        cookies = res.cookies.get_dict()

        if res.json()['code'] == 200:
            self.logger.info('登录成功! ')
            self.logger.info('Hello, {}!'.format(res.json()['profile']['nickname']))
            self.redis_client.save_cookies(self.site, self.username, cookies)
            return cookies
        elif res.json()['message'] == '密码错误':
            self.reset_flag = True
            raise Exception('账号或密码错误! ')
        raise Exception('登录失败: {} '.format(res.json()['message']))

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
    x = WangyiyunLogin().run(load_cookies=False)
    print(x)
