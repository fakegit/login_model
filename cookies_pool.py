# -*- coding: utf-8 -*-
# @Time    : 2019/7/27 21:18
# @Author  : xuzhihai0723
# @Email   : 18829040039@163.com
# @File    : redies_db.py
# @Software: PyCharm

from utils import *


class RedisClient:

    def __init__(self, logger):
        self.redis_client = get_redis_client()
        self.logger = logger

    def load_cookies(self, site, username):
        """
        从数据库读取 cookies
        :return:
        """
        cookies = self.redis_client.hget('cookies:{}'.format(site), username)

        if cookies:
            try:
                self.logger.info('从数据库读取 Cookies ...')
                cookies = json.loads(cookies)
            except ValueError:
                cookies = json.loads(json.dumps(ast.literal_eval(cookies)))
            self.logger.info('读取到 Cookies ! ')
            return cookies
        else:
            self.logger.warning('未从数据库中读取到 Cookies !')
            return False

    def save_cookies(self, site, username, cookies):
        """
        将 cookies 写入到数据库中
        :return:
        """
        self.logger.info('将 cookies 保存到数据库中...')
        cookies_str = json.dumps(cookies)
        self.redis_client.hset('cookies:{}'.format(site), username, cookies_str)
        self.logger.info('保存完成!')
