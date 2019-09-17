# -*- coding: utf-8 -*-
# @Time    : 2019/8/5 23:55
# @Author  : Esbiya
# @Email   : 18829040039@163.com
# @File    : zhilian_login.py
# @Software: PyCharm


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains
from utils import *
import requests
from cookies_pool import RedisClient
from PIL import Image
from io import BytesIO

THRESHOLD = 60
LEFT = 60
BORDER = 0


class ZhilianLogin:

    def __init__(self, username: str = None, password: str = None):
        self.site = 'zhilian'
        self.logger = get_logger()
        self.username = username
        self.password = password
        self.redis_client = RedisClient(self.logger)
        self.browser = None
        self.wait = None

    def check_islogin(self, cookies):
        """
        检查登录状态, 跳转至个人主页则 cookies 有效
        :param cookies:
        :return:
        """
        url = 'https://fe-api.zhaopin.com/c/i/user/detail'
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.80 Safari/537.36'
        }
        res = requests.get(url, headers=headers, cookies=cookies).json()
        if res['code'] == 200:
            self.logger.info('Cookies 有效!')
            nickname = res['data']['Name']
            self.logger.info('Hello, {}! '.format(nickname))
            return True
        return False

    def get_geetest_button(self):
        button = self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'geetest_slider_button')))
        return button

    def get_geetest_image(self, name, full):
        top, bottom, left, right, size = self.get_position(full)
        # print("验证码位置", top, bottom, left, right)
        screenshot = self.get_screenshot()
        captcha = screenshot.crop(
            (left, top, right, bottom))
        size = size["width"] - 1, size["height"] - 1
        captcha.thumbnail(size)
        # captcha.show()
        # captcha.save(name)
        return captcha

    def get_position(self, full):
        img = self.wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, "canvas.geetest_canvas_slice")))
        fullbg = self.wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, "canvas.geetest_canvas_fullbg")))
        time.sleep(2)

        # 两种执行js写法
        if full:
            self.browser.execute_script(
                'document.getElementsByClassName("geetest_canvas_fullbg")[0].setAttribute("style", "")')
        else:
            self.browser.execute_script(
                "arguments[0].setAttribute(arguments[1], arguments[2])", fullbg, "style", "display: none")

        location = img.location
        size = img.size
        top, bottom, left, right = location["y"], location["y"] + \
                                   size["height"], location["x"], location["x"] + size["width"]
        return (top, bottom, left, right, size)

    def get_screenshot(self):
        screenshot = self.browser.get_screenshot_as_png()
        return Image.open(BytesIO(screenshot))

    def get_gap(self, image1, image2):
        for i in range(LEFT, image1.size[0]):
            for j in range(image1.size[1]):
                if not self.is_pixel_equal(image1, image2, i, j):
                    return i
        return LEFT

    def is_pixel_equal(self, image1, image2, x, y):
        pixel1 = image1.load()[x, y]
        pixel2 = image2.load()[x, y]
        if abs(pixel1[0] - pixel2[0]) < THRESHOLD and abs(pixel1[1] - pixel2[1]) < THRESHOLD and abs(
                pixel1[2] - pixel2[2]) < THRESHOLD:
            return True
        else:
            return False

    def get_track(self, distance):
        """
        获取滑块移动轨迹的列表
        :param distance: 第二个缺块的左侧的x坐标
        :return: 滑块移动轨迹列表
        """
        # 移动轨迹
        track = []
        # 当前位移
        current = 0
        # 减速阈值
        mid = distance * 2 / 3
        # 计算间隔
        t = 0.4
        # 初速度
        v = 0
        distance += 10  # 使滑块划过目标地点, 然后回退

        while current < distance:
            # 加速度
            if current < mid:
                a = 2
            else:
                a = -3
            # 初速度 v0
            v0 = v
            # 当前速度
            v = v0 + a * t
            # 移动距离
            move = v0 * t + 0.5 * a * t * t
            # 当前位移
            current += move
            track.append(move)

        return track

    def get_slider(self):
        return self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "geetest_slider_button")))

    def move_to_gap(self, button, track):
        ActionChains(self.browser).click_and_hold(button).perform()
        for x in track:
            ActionChains(self.browser).move_by_offset(xoffset=x, yoffset=0).perform()
            # time.sleep(0.5)
        # time.sleep(0.5)
        ActionChains(self.browser).release().perform()

    @seleniumLoopUnlessSeccessOrMaxTry(3, sleep_time=3)
    def login(self):
        """
        打开浏览器,并且输入账号密码
        :return: None
        """
        self.logger.info('尝试登录...')
        self.browser.get("https://passport.zhaopin.com/login?bkUrl=%2F%2Fi.zhaopin.com%2Fblank%3Fhttps%3A%2F%2Fwww.zhaopin.com%2F")
        time.sleep(1)
        self.browser.find_element_by_xpath('//li[@class="zppp-panel-tab"]').click()
        time.sleep(1)
        username = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[type="text"]')))
        password = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[type="password"]')))
        submit = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.zppp-submit')))
        time.sleep(1)
        username.clear()
        username.send_keys(self.username)
        time.sleep(1)
        password.clear()
        password.send_keys(self.password)
        time.sleep(1)
        self.logger.info('账号密码输入完成, 点击登录按钮')
        submit.click()

        self.logger.info('等待验证码加载...')
        image1 = self.get_geetest_image("captcha1.png", True)
        image2 = self.get_geetest_image("captcha2.png", False)
        gap = self.get_gap(image1, image2)
        track = self.get_track(gap - BORDER)
        slider = self.get_slider()
        self.logger.info('移动滑块至缺口...')
        self.move_to_gap(slider, track)
        time.sleep(3)

        # 跳转至首页则登录成功
        self.logger.info('校验滑动验证是否成功...')
        if self.browser.current_url == 'https://www.zhaopin.com/':
            self.logger.info('校验完成, 登录成功! ')
            nickname = self.browser.find_element_by_css_selector('.zp-userinfo').text
            self.logger.info('Hello, {}! '.format(nickname))
            cookies = self.browser.get_cookies()
            cookies = {item['name']: item['value'] for item in cookies}
            self.redis_client.save_cookies(self.site, self.username, cookies)
            self.browser.close()
            return True
        elif self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "canvas.geetest_canvas_slice"))):
            raise Exception('滑动验证失败! ')
        elif self.browser.find_element_by_xpath('//p[@class="tips"]'):
            self.logger.error('校验完成, 登录失败: {}! '.format(self.browser.find_element_by_xpath('//p[@class="tips"]').text))
            return False

    @check_user()
    def run(self, load_cookies: bool = True):
        if load_cookies:
            cookies = self.redis_client.load_cookies(self.site, self.username)
            if cookies:
                if self.check_islogin(cookies):
                    return True
                self.logger.warning('Cookies 已过期')

        options = webdriver.ChromeOptions()
        # 设置为开发者模式，避免被识别
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        options.add_argument('--headless')
        self.browser = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.browser, 20)
        self.login()
        self.logger.info('程序结束！')


if __name__ == '__main__':
    ZhilianLogin().run(load_cookies=False)
