# -*- coding: utf-8 -*-
# @Time    : 2019/11/2 13:33
# @Author  : Esbiya
# @Email   : 18829040039@163.com
# @File    : encrypt.py
# @Software: PyCharm

import sys

sys.path.append('../..')

import hmac
import hashlib
import base64
import json
import random
import time
import execjs
from Crypto.Cipher import AES
from Crypto.Cipher import PKCS1_v1_5 as Cipher_pkcs1_v1_5
from Crypto.PublicKey import RSA
from binascii import b2a_base64, b2a_hex


def rsa_encrypt(text, pub_key):
    """
    RSA 加密
    :param text: 明文
    :param pub_key: 公钥
    :return:
    """
    public_key = '\n'.join([
        "-----BEGIN PUBLIC KEY-----",
        pub_key,
        "-----END PUBLIC KEY-----"
    ])
    rsa_key = RSA.importKey(public_key)
    encrypter = Cipher_pkcs1_v1_5.new(rsa_key)
    cipher = base64.b64encode(encrypter.encrypt(text.encode()))
    return cipher.decode()


def sha256_encrypt(text, type='hex'):
    """
    sha256加密
    :param text:
    :param type: 返回字符串类型
    :return:
    """
    sha256 = hashlib.sha256()
    sha256.update(text.encode())
    if type == 'hex':
        return sha256.hexdigest()
    elif type == 'base64':
        return base64.b64encode(sha256.digest()).decode()


def hmac_sha256(text, key, type='hex'):
    """
    hMac sha256 加密
    :param text:
    :param key:
    :param type:
    :return:
    """
    cipher = hmac.new(key.encode(), text.encode(), digestmod=hashlib.sha256)
    if type == 'base64':
        return base64.b64encode(cipher.digest()).decode()
    return cipher.hexdigest()


def md5_encrypt(text, type='hex'):
    """
    md5 加密
    :param text:
    :param type:
    :return:
    """
    md5 = hashlib.md5()
    md5.update(text.encode())
    if type == 'base64':
        return base64.b64encode(md5.digest()).decode()
    return md5.hexdigest()


def aes_encrypt(publick_key, password, iv):
    """
    不知道是不是AES, 因为 iv 长度不足16位, 但是 js 里面命名为 AES
    :param publick_key:
    :param password:
    :param iv:
    :return:
    """
    with open('163yun_crypt.js', 'rb') as f:
        js = f.read().decode()
    ctx = execjs.compile(js)

    md5_pass = md5_encrypt(password)
    return ctx.call('encryptPassword', publick_key, md5_pass, iv)


def generate_nonce(num=64):
    """
    根据当前时间戳生成指定长度字符串
    :param num:
    :return:
    """
    nonce = ''
    for i in range(2):
        t = random.random() * 9007199254740992
        n = sha256_encrypt(str(t + int(time.time() * 1000)), 'base64')
        nonce += n
    return nonce[:num]
