# -*- coding: utf-8 -*-
# @Time    : 2019/9/21 14:55
# @Author  : Esbiya
# @Email   : 18829040039@163.com
# @File    : jd_login.py
# @Software: PyCharm


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains
from bs4 import BeautifulSoup
from utils import *
import requests
import re
import cv2
import base64
import random
import numpy as np
from cookies_pool import RedisClient
from PIL import Image


class JDLogin:

    def __init__(self, username: str = None, password: str = None):
        self.site = 'jingdong'
        self.logger = get_logger()
        self.username = username
        self.password = password
        self.redis_client = RedisClient(self.logger)
        self.browser = None
        self.wait = None

        # 密码错误重置初始化
        self.reset_flag = False

    def check_islogin(self, cookies):
        """
        检查登录状态, 请求个人主页未跳转至登录页则 cookies 有效
        :param cookies:
        :return:
        """
        url = 'http://i.jd.com/user/info'
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.80 Safari/537.36'
        }
        resp = requests.get(url, headers=headers, cookies=cookies)
        if url in resp.url:
            self.logger.info('Cookies 有效!')
            bsobj = BeautifulSoup(resp.text, 'lxml')
            nickname = bsobj.select('#hiddenAliasName')[0]['value']
            self.logger.info('Hello, {}! '.format(nickname))
            return True
        return False

    def download_img(self, url, type):
        """
        下载验证码图片
        :param url: 图片 base64
        :param type: 类型
        :return:
        """
        img_db_path = os.path.abspath('...') + r'\img_db'
        if not os.path.exists(img_db_path):
            os.mkdir(img_db_path)
        img_path = img_db_path + '\\' + type + '.jpg'
        try:
            if os.path.exists(img_path):
                os.remove(img_path)
            data = url.split(',')[1]
            img = base64.b64decode(data)
            with open(img_path, "wb") as f:
                f.write(img)
            return img_path
        except Exception as e:
            self.logger.error("验证码图片获取失败! ", e.args)

    def get_distance(self, slider_url, captcha_url):
        """
        获取缺口距离
        :param slider_url: 滑块图片 base64
        :param captcha_url: 验证码图片 base64
        :return:
        """
        # 引用上面的图片下载
        slider_path = self.download_img(slider_url, 'slider')

        time.sleep(2)

        # 引用上面的图片下载
        captcha_path = self.download_img(captcha_url, 'captcha')

        # # 计算拼图还原距离
        target = cv2.imread(slider_path, 0)
        template = cv2.imread(captcha_path, 0)
        w, h = target.shape[::-1]
        # print(w, h)
        temp = os.path.abspath('...') + r'\img_db' + '\\' + 'temp.jpg'
        targ = os.path.abspath('...') + r'\img_db' + '\\' + 'targ.jpg'
        cv2.imwrite(temp, template)
        cv2.imwrite(targ, target)
        target = cv2.imread(targ)
        target = cv2.cvtColor(target, cv2.COLOR_BGR2GRAY)
        target = abs(255 - target)
        cv2.imwrite(targ, target)
        target = cv2.imread(targ)
        template = cv2.imread(temp)
        result = cv2.matchTemplate(target, template, cv2.TM_CCOEFF_NORMED)
        x, y = np.unravel_index(result.argmax(), result.shape)
        # 缺口位置
        # print((y, x, y + w, x + h))

        # 调用PIL Image 做测试
        image = Image.open(captcha_path)

        xy = (y, x, y + w, x + h)
        # 切割
        imagecrop = image.crop(xy)
        # 保存切割的缺口
        imagecrop.save(os.path.abspath('...') + r'\img_db' + '\\' + "new_image.png")
        # imagecrop.show()
        return y

    def get_slider(self):
        """
        获取滑块
        :return:
        """
        return self.wait.until(EC.element_to_be_clickable((By.XPATH, '//div[contains(@class, "JDJRV-slide-btn")]')))

    def move_to_gap(self, distance, slider):
        """
        移动滑块至缺口
        :param distance:
        :param slider:
        :return:
        """
        has_gone_dist = 0
        remaining_dist = distance
        # distance += randint(-10, 10)
        # 按下鼠标左键
        ActionChains(self.browser).click_and_hold(slider).perform()
        time.sleep(0.5)
        while remaining_dist > 0:
            ratio = remaining_dist / distance
            if ratio < 0.1:
                # 开始阶段移动较慢
                span = random.randint(3, 5)
            elif ratio > 0.9:
                # 结束阶段移动较慢
                span = random.randint(5, 8)
            else:
                # 中间部分移动快
                span = random.randint(15, 20)
            ActionChains(self.browser).move_by_offset(span, random.randint(-5, 5)).perform()
            remaining_dist -= span
            has_gone_dist += span
            time.sleep(random.randint(5, 20) / 100)

        ActionChains(self.browser).move_by_offset(remaining_dist, random.randint(-5, 5)).perform()
        ActionChains(self.browser).release(on_element=slider).perform()

    def is_element_exists(self, element):
        """
        判断页面元素是否存在: Xpath
        :param element:
        :return:
        """
        try:
            self.browser.find_element_by_xpath(element)
            return True
        except:
            return False

    @seleniumLoopUnlessSeccessOrMaxTry(3, sleep_time=3)
    def login(self):
        """
        打开浏览器,并且输入账号密码
        :return: None
        """
        self.logger.info('尝试登录...')
        # 打开京东网站
        self.browser.get('https://passport.jd.com/new/login.aspx')

        # 点击选择账号密码登录
        self.logger.info('点击选择账号密码登录...')
        acount_login = self.wait.until(
            EC.presence_of_element_located((By.XPATH, '//div[contains(@class, "login-tab-r")]')))
        acount_login.click()

        self.logger.info('输入账号...')
        input_username = self.wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="loginname"]')))
        input_username.send_keys(self.username)

        time.sleep(1)

        self.logger.info('输入密码...')
        input_password = self.wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="nloginpwd"]')))
        input_password.send_keys(self.password)

        time.sleep(1)

        self.logger.info('点击登录...')
        button = self.wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="loginsubmit"]')))
        button.click()
        # 判断是否有滑动页面
        slider_flag = self.is_element_exists('//*[@id="JDJRV-wrap-loginsubmit"]/DIV/DIV/DIV/DIV[1]/DIV[2]/DIV[1]/IMG')
        if not slider_flag:
            self.logger.info('未出现滑块验证! ')
            time.sleep(3)
            error_flag = self.is_element_exists('//div[@class="msg-error"]')
            if error_flag:
                msg_error = self.browser.find_element_by_xpath('//div[@class="msg-error"]').text
                if msg_error == '账户名与密码不匹配，请重新输入':
                    self.reset_flag = True
                    raise Exception('账号或密码错误! ')
                else:
                    self.logger.error(msg_error)
                    return None
            elif self.browser.current_url != "https://www.jd.com/":
                self.logger.error('登录失败! ')
                return None
            else:
                self.logger.info('登录成功! ')
                cookies = self.browser.get_cookies()
                cookies = {cookie['name']: cookie['value'] for cookie in cookies}
                self.redis_client.save_cookies(self.site, self.username, cookies)
                return cookies
        self.logger.info('出现滑块验证! ')
        while True:
            captcha_b64data = self.wait.until(EC.presence_of_element_located(
                (By.XPATH, '//div[@class="JDJRV-bigimg"]/img'))).get_attribute('src')
            slider_b64data = self.wait.until(EC.presence_of_element_located(
                (By.XPATH, '//div[@class="JDJRV-smallimg"]/img'))).get_attribute('src')
            distance = self.get_distance(slider_b64data, captcha_b64data)
            # print(distance)
            # 网页上的尺寸差
            distance = distance * (279 / 360)
            slider = self.get_slider()
            self.move_to_gap(distance, slider)
            time.sleep(3)
            error_flag = self.is_element_exists('//div[@class="msg-error"]')
            if error_flag:
                msg_error = self.browser.find_element_by_xpath('//div[@class="msg-error"]').text
                if msg_error == '账户名与密码不匹配，请重新输入':
                    self.reset_flag = True
                    raise Exception('账号或密码错误! ')
                else:
                    self.logger.error(msg_error)
                    return None
            elif self.is_element_exists('//div[@class="JDJRV-bigimg"]/img'):
                self.logger.warning('验证失败, 重试! ')
                time.sleep(0.5)
            else:
                self.logger.info('验证通过, 登录成功! ')
                cookies = self.browser.get_cookies()
                cookies = {cookie['name']: cookie['value'] for cookie in cookies}
                self.redis_client.save_cookies(self.site, self.username, cookies)
                return cookies
            time.sleep(5)

    @check_user()
    def run(self, load_cookies: bool = True):
        if load_cookies:
            cookies = self.redis_client.load_cookies(self.site, self.username)
            if cookies:
                if self.check_islogin(cookies):
                    return cookies
                self.logger.warning('Cookies 已过期')

        options = webdriver.ChromeOptions()
        # 设置为开发者模式，避免被识别, 开发者模式下 webdriver 属性为 undefined
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        # options.add_argument('--headless')
        self.browser = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.browser, 20)
        cookies = self.login()
        self.logger.info('程序结束！')
        return cookies


if __name__ == '__main__':
    x = JDLogin().run(load_cookies=True)
    print(x)
