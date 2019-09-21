# -*- coding: utf-8 -*-
# @Time    : 2019/9/19 20:18
# @Author  : Esbiya
# @Email   : 18829040039@163.com
# @File    : server.py
# @Software: PyCharm

from flask import Flask, jsonify, request
from gevent.pywsgi import WSGIServer
# 需要在这里导入登录脚本
from weibo.weibo_login import WeiboLogin

__all__ = ['app']

app = Flask(__name__)

# 示例: 在这个字典添加想要用API服务的站点
WEBSITE_MAP = {
    'weibo': 'WeiboLogin',
}


def main(address="0.0.0.0", port=8778):
    http_server = WSGIServer((address, port), app)
    http_server.serve_forever()


@app.route('/')
def root():
    return '<h2>Welcome to Cookies Server System</h2>'


@app.route('/get', methods=['POST'])
def get_cookie():
    """
    获取 cookie
    :return:
    """
    if all([key in request.form for key in {'website', 'username', 'password'}]):
        cls = WEBSITE_MAP.get(request.form.get('website', None), None)
        if not cls:
            return jsonify({
                'code': -3,
                'message': 'Invalid Website! ',
                'data': None
            })
        getter = eval(
            cls + '(username="' + request.form.get('username') + '", password="' + request.form.get('password') + '")')
        result = getter.run()
        del getter
        if result:
            return jsonify({
                'code': 1,
                'message': 'success',
                'data': {
                    'cookies': result
                }
            })
        return jsonify({
            'code': -1,
            'message': 'fail',
            'data': None
        })
    else:
        return jsonify({
            'code': -2,
            'message': 'Invalid Parameter! ',
            'data': None
        })


if __name__ == '__main__':
    main()
