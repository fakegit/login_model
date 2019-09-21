# -*- coding: utf-8 -*-
# @Time    : 2019/7/27 9:51
# @Author  : Esbiya
# @Email   : 18829040039@163.com
# @File    : utils.py
# @Software: PyCharm


import os
import ast
import time
import json
import traceback
import redis
import logging
import functools


def get_logger(name=__file__, level=logging.INFO, logfile=None):
    """
    获取logger
    :param name: 名称
    :param level: log等级
    :return:
    """
    name = name.split('/')[-1]
    logger = logging.getLogger(name)
    logger.setLevel(level)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s: - %(message)s',
                                  datefmt='%Y-%m-%d %H:%M:%S')
    ch = logging.StreamHandler()
    ch.setLevel(level)
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    root_path = 'log'
    if not os.path.exists(root_path):
        os.mkdir(root_path)
    if logfile is None:
        logfile = '{}/{}.log'.format(root_path, time.strftime('%Y-%m-%d', time.localtime(time.time())))
    else:
        logfile = '{}/{}'.format(root_path, logfile)
    fh = logging.FileHandler(logfile)
    fh.setLevel(level)
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    return logger


def loopUnlessSeccessOrMaxTry(max_times, sleep_time=1.5):
    """
    重试修饰器，被该修饰器修饰的函数，出错后会循环执行，
    直到执行成功或者到达最大执行次数
    :param max_times: 最大执行次数
    :param sleep_time:出错后的暂停时间
    :return:
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            err_cnt = 1
            reset_cnt = 1
            while True:
                try:
                    result = func(self, *args, **kwargs)
                    return result
                except Exception as e:
                    if self.reset_flag:
                        if reset_cnt >= max_times:
                            self.logger.error('密码错误次数过多, 请确认密码后重新登录! ')
                            break
                        self.logger.warning('账号或密码错误, 你还有{}次机会! '.format(max_times - reset_cnt))
                        self.username = input('账号 >> \n')
                        self.password = input('密码 >> \n')
                        reset_cnt += 1
                        self.reset_flag = False
                        time.sleep(sleep_time)
                        continue
                    else:
                        self.logger.warning('在执行函数: {} 时出错 -> {}'.format(func.__name__, e))
                    time.sleep(sleep_time)
                if err_cnt >= max_times:
                    self.logger.error('在执行函数: {} 时出错次数过多, 请重新运行程序! '.format(func.__name__))
                    break
                err_cnt += 1

        return wrapper

    return decorator


def seleniumLoopUnlessSeccessOrMaxTry(max_times, sleep_time=1):
    """
    重试修饰器，被该修饰器修饰的函数，出错后会循环执行，
    直到执行成功或者到达最大执行次数
    :param max_times: 最大执行次数
    :return:
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            err_cnt = 1
            reset_cnt = 1
            while True:
                try:
                    return func(self, *args, **kwargs)
                except Exception as e:
                    if self.reset_flag:
                        if reset_cnt >= max_times:
                            self.logger.error('密码错误次数过多, 请确认密码后重新登录! ')
                            break
                        self.logger.warning('账号或密码错误, 你还有{}次机会! '.format(max_times - reset_cnt))
                        self.username = input('账号 >> \n')
                        self.password = input('密码 >> \n')
                        reset_cnt += 1
                        self.reset_flag = False
                        continue
                    else:
                        self.logger.warning('在执行函数: {} 时出错 -> {}'.format(func.__name__, e))
                    self.browser.execute_script('window.stop()')
                    time.sleep(1)
                    self.browser.refresh()
                    time.sleep(sleep_time)
                if err_cnt >= max_times:
                    self.logger.error(u'出错次数过多，该函数{}已跳过执行'.format(func.__name__))
                    break
                err_cnt += 1

        return wrapper

    return decorator


async def pyppeteerLoopUnlessSeccessOrMaxTry(max_times, sleep_time=1):
    """
    重试修饰器，被该修饰器修饰的函数，出错后会循环执行，
    直到执行成功或者到达最大执行次数
    :param max_times: 最大执行次数
    :return:
    """

    async def decorator(func):
        @functools.wraps(func)
        async def wrapper(self, *args, **kwargs):
            cnt = 1
            while True:
                try:
                    return func(self, *args, **kwargs)
                except Exception as e:
                    self.logger.error(u'在执行函数{}时出错 {}'.format(func.__name__, e))
                    # traceback.print_exc()
                    await self.page_close()
                    time.sleep(sleep_time)
                if cnt >= max_times:
                    self.logger.error(u'出错次数过多，该函数{}已跳过执行'.format(func.__name__))
                    break
                cnt += 1

        return wrapper

    return decorator


def check_login():
    """
    检查是否登录
    :return:
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            # 读取并装载cookies
            self.load_cookies()
            # 检查是否已经登录了
            self.check_islogin()
            # 状态正常
            if self.is_login:
                self.logger.info('登录状态正常！')
                return func(self, *args, **kwargs)
            # 不正常则重新登录
            else:
                self.login()

        return wrapper

    return decorator


def check_user():
    """
    检查账号密码
    :return:
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            if not self.username:
                self.username = input('账号 >> \n')
            if not self.password:
                self.password = input('密码 >> \n')

            return func(self, *args, **kwargs)

        return wrapper

    return decorator


def reset_user():
    """
    重置账号密码
    :return:
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            if self.reset_flag:
                if self.reset_num < self.max_reset_num:
                    self.username = input('账号 >> \n')
                    self.password = input('密码 >> \n')
                else:
                    self.logger.warning('密码输入次数达到最大限制, 请确认密码重新运行程序！ ')
            return func(self, *args, **kwargs)

        return wrapper

    return decorator


def load_cookies():
    """
    加载 Cookies 到 Session
    :return:
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            try:
                self.session.cookies.load(ignore_discard=True)
                return func(self, *args, **kwargs)
            except FileNotFoundError:
                return False

        return wrapper

    return decorator


def get_redis_client():
    client = redis.StrictRedis(
        host='127.0.0.1',
        port=6379,
        db=0,
        password=None)
    return client


def parse_json(s):
    begin = s.find('{')
    end = s.rfind('}') + 1
    return json.loads(s[begin:end])
