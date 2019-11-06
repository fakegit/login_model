# -*- coding: utf-8 -*-
# @Time    : 2019/11/2 14:27
# @Author  : Esbiya
# @Email   : 18829040039@163.com
# @File    : 163yun_login.py
# @Software: PyCharm

import sys
sys.path.append('../..')

import time
import requests
from encrypt import *
import traceback

session = requests.session()
session.headers = {
    'Referer': 'https://id.163yun.com/login?referrer=https://dun.163.com/dashboard&h=yd&t=yd&i18nEnable=true&locale=zh_CN&fromyd=baiduP2_YZM_CP3662',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.80 Safari/537.36'
}

a = generate_nonce()
i = generate_nonce(16)


def init_login():
    url = 'https://id.163yun.com/s/ngt'

    session.headers.update({
        'If-Modified-Since': '0',
        'Content-Type': 'application/x-www-form-urlencoded',
        "Cache-Control": "no-cache",
        'Pragma': 'no-cache',
    })

    r = rsa_encrypt(
        a + "^$$^" + i,
        "MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCGMAi8lnyTZ1ux0UUlaFgmoOnS8JFoKuELktYOdbP33KqQ6pl0SemI1kzxQQb5ByzmIxcPpHJy3407AEpardXEm0FpeaonTQXk4dqyCv6XS8wjx+UXu5nSy6xSlxMEkg1E37xEHNL4hUvzMnxlOci3VCNLrbvkmJj6PaNwXrTdjwIDAQAB"
    )
    data = {
        'k': a,
        'j': r
    }
    try:
        resp = session.post(url, data=data).json()
        return resp
    except:
        traceback.print_exc()


def check_init(init_key):
    c = sha256_encrypt(i).lower() + '=='
    f = hmac_sha256(init_key['n'] + init_key['h'], c, 'base64')
    if f == init_key['q']:
        return {
            'rk': a,
            'pk': i,
            'hexpk': c,
            'st': init_key['h'],
            'iv': init_key['w'],
            'ct': int(time.time() * 1000)
        }
    return False


def generate_signature(init_data):
    n = init_data['ct']
    a = int(time.time() * 1000)
    r = generate_nonce()
    if not n or a - int(n) <= 0 or a - int(n) > 3540000:
        signature = hmac_sha256(r + init_data['st'], sha256_encrypt(init_data['pk']).lower() + '==', 'base64')
    else:
        s = int(init_data['st']) + a - int(n)
        signature = hmac_sha256(r + str(s), sha256_encrypt(init_data['pk'], 'base64'))
    return {
        'time': init_data['st'],
        'redisKey': init_data['rk'],
        'publicKey': init_data['pk'],
        'hexPublicKey': init_data['hexpk'],
        'iv': init_data['iv'],
        'nonce': r,
        'signature': signature
    }


def login(init_key, username, password):
    url = 'https://id.163yun.com/accounts/login?i18nEnable=true'

    n = generate_nonce()
    data = {
        'r': username,
        'u': aes_encrypt(init_key['publicKey'], password, init_key['iv']),
        'v': "Am4IH9C6zz-EaWPYsKTCRPF9t2ZVo2rbv7Xcqe9TiUVO8RspnLIgg7VrzQ5iujf2ogWi6coIn.o7zGbYfuZY5rHEOhwGFmUobZRBSc-mAznGtGhrLjmK.6_vb4Cbl15dS9hcat_C0lESIv94FTmMOYDszKAzC9hfUZsZ---56Ouxf_frPV7ItLiwGud.mFYs.MlMFBUDxkuftjBTCN-g52ZLm2d0m5SR-pI9xYryxW7hhZSrQyJrKRZKlTFnowvTfwexc8FHGl4JzkmZhVcvwaFN_chhR8Ib67XuQYxB5yjHfmK4i45q9wR.PDmG6ZGjxUvL27rQveptApBJB7OQ0zW5.2fAgK5BK4bs_gJXAyi1K0QoHgrkkE9sl1sCmI9zBQGuIxJVfvS3",
        'h': 'yd',
        'referer': 'https://dun.163.com/dashboard',
        'g': init_key['redisKey'],
        'n': n,
        't': init_key['time'],
        's': hmac_sha256(n + init_key['time'], init_key['hexPublicKey'], 'base64')
    }
    resp = session.post(url, data=data)
    print(resp.text)


if __name__ == '__main__':
    x = init_login()
    y = check_init(x)
    z = generate_signature(y)
    login(z, '18829040039', 'xuzhihai0723')
