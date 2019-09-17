# -*- coding: utf-8 -*-
# @Time    : 2019/7/28 17:05
# @Author  : xuzhihai0723
# @Email   : 18829040039@163.com
# @File    : meituan_login.py
# @Software: PyCharm

import asyncio
import random
from utils import *
from chaojiying import *
from retrying import retry
from cookies_pool import RedisClient
from pyppeteer.launcher import launch


class MeituanLogin:

    def __init__(self, username: str = None, password: str = None):
        self.site = 'meituan'
        self.logger = get_logger()
        self.username = username
        self.password = password
        self.redis_client = RedisClient(self.logger)

        # 密码错误重置初始化
        self.reset_flag = False

    def check_islogin(self, cookies):
        url = 'https://www.meituan.com/ptapi/getLoginedUserInfo?timestamp={}'.format(int(time.time() * 1000))
        headers = {
            'Referer': 'http://hf.meituan.com/',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.80 Safari/537.36'
        }
        cookies = {item['name']: item['value'] for item in cookies}
        resp = requests.get(url, headers=headers, cookies=cookies).json()
        if resp['nickName']:
            self.logger.info('Cookies 有效! ')
            nickname = resp['nickName']
            self.logger.info('Hello, {}! '.format(nickname))
            return True
        return False

    @staticmethod
    def input_time_random():
        return random.randint(150, 201)

    def retry_if_exception(self, result):
        if isinstance(result, Exception):
            self.logger.error('Something Wring: {}'.format(result))
            return result is Exception
        return result is None

    async def page_evaluate(self, page):

        await page.evaluate(
            '''() =>{ Object.defineProperties(navigator,{ webdriver:{ get: () => undefined } }) }''')  # 以下为插入中间js，将淘宝会为了检测浏览器而调用的js修改其结果。
        await page.evaluate('''() =>{ window.navigator.chrome = { runtime: {},  }; }''')
        await page.evaluate(
            '''() =>{ Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] }); }''')
        await page.evaluate(
            '''() =>{ Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5,6], }); }''')

    async def mouse_slide(self, page=None):
        await asyncio.sleep(2)
        try:
            # 鼠标移动到滑块，按下，滑动到头（然后延时处理），松开按键
            await page.hover('#yodaBox')  # 不同场景的验证码模块可能名字不同。
            await page.mouse.down()  # 模拟按下鼠标
            await page.mouse.move(2000, 0, {'delay': random.randint(1000, 2000)})  # js模拟拖动
            await page.mouse.up()  # 模拟松开鼠标
        except Exception as e:
            return None, page
        else:
            await asyncio.sleep(2)
            slider_again = await page.Jeval('#yodaTip', 'node => node.textContent')  # 判断是否通过
            if slider_again != '验证码已发送，请稍后':
                return None, page
            else:
                # await page.screenshot({'path': './headless-slide-result.png'}) # 截图测试
                return 1, page

    @staticmethod
    async def page_close(browser):
        """
        关闭浏览器驱动
        :param browser:
        :return:
        """
        for _page in await browser.pages():
            await _page.close()
        await browser.close()

    async def login(self):
        # 以下使用await 可以针对耗时的操作进行挂起
        # 记：一定要给pyppeteer权限删除用户数据, 即设置userDataDir: 文件夹名称, 否则会报错无法移除用户数据
        browser = await launch(
            {
                'headless': False,
                'args': ['--no-sandbox', '--disable-infobars'],
            },
            userDataDir=r'D:\login\userdata',
            args=['--window-size=1366, 768']
        )
        page = await browser.newPage()  # 启动个新的浏览器页面
        await page.setJavaScriptEnabled(enabled=True)  # 启用js
        await page.setUserAgent(
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 Edge/16.16299'
        )  # 设置模拟浏览器

        self.logger.info('尝试登录...')

        await page.goto('https://passport.meituan.com/account/unitivelogin?service=www&continue=https%3A%2F%2Fwww.meituan.com%2Faccount%2Fsettoken%3Fcontinue%3Dhttp%253A%252F%252Fhf.meituan.com%252F')

        await self.page_evaluate(page)

        self.logger.info('输入账号密码...')
        await page.type('#login-email', self.username, {'delay': self.input_time_random() - 50})
        time.sleep(1)
        await page.type('#login-password', self.password, {'delay': self.input_time_random()})
        time.sleep(1)

        self.logger.info('点击提交...')
        await page.click('input.btn')
        time.sleep(2)

        await self.verify(page)

    @staticmethod
    async def get_position(captcha):
        """
        获取验证码位置元组
        :return:
        """
        location = captcha.location
        size = captcha.size
        top, bottom, left, right = location["y"], location["y"] + \
                                   size["height"], location["x"], location["x"] + size["width"]
        return top, bottom, left, right, size

    async def verify(self, page):
        """
        风控认证
        :param page:
        :return:
        """
        self.logger.info('判断是否需要进行风控认证')
        await asyncio.sleep(3)
        if await page.xpath('//img[@id="yodaImgCode"]'):
            self.logger.info('账号存在风险, 需要进行风控认证! ')
            await page.screenshot({'path': './captcha_screenshot.png'})
            # captcha = (await page.xpath('//img[@id="yodaImgCode"]'))[0]
            # top, bottom, left, right, size = await self.get_position(captcha)
            with open('captcha_screenshot.png', 'rb') as f:
                img_data = f.read()
            # img_data = screenshot.crop((left, top, right, bottom))
            self.logger.info('使用超级鹰识别验证码...')
            ok, verify_code = image_to_text(img_data)
            if ok:
                self.logger.info('成功识别验证码! ')
                self.logger.info('输入验证码...')
                await page.type('#yodaImgCodeInput', verify_code, {'delay': self.input_time_random() - 50})
                await asyncio.sleep(1)
                self.logger.info('点击提交...')
                await page.click('#yodaImgCodeSure')
                await asyncio.sleep(3)
        else:
            self.logger.info('账号正常, 未出现验证码! ')
            await asyncio.sleep(3)
            if page.url == 'http://hf.meituan.com/':
                self.logger.info('登录成功! ')
                cookies = await page.cookies()
                self.redis_client.save_cookies(self.site, self.username, cookies)
                return True
            elif 'verify.meituan.com' in page.url:
                self.logger.warning('为了您的账户安全，请先验证手机! ')
                await page.click('#yodaSmsCodeBtn')
                await asyncio.sleep(3)
                slider = page.Jeval('#yodaBox', 'node => node.style')
                if slider:
                    self.logger.info('出现滑块情况判定')
                    flag = await self.mouse_slide(page=page)
                    if flag:
                        self.logger.info('验证通过! ')
                    else:
                        self.logger.error('滑块验证失败! ')
                        return False
                await asyncio.sleep(3)
                phone_vcode = input('请输入手机验证码 >> \n')
                await page.type('#yodaVerification', phone_vcode, {'delay': self.input_time_random() - 50})
                await asyncio.sleep(1)
                self.logger.info('点击提交...')
                await page.click('#yodaSubmit')
                await asyncio.sleep(2)
        if await page.xpath('//div[@class="validate-info"]'):
            validate_info = await (await (await page.xpath('//div[@class="validate-info"]'))[0].getProperty('textContent')).jsonValue()
            self.logger.error(validate_info)
            return False
        elif page.url == 'http://hf.meituan.com/':
            self.logger.info('登录成功! ')
            cookies = await page.cookies()
            self.redis_client.save_cookies(self.site, self.username, cookies)
            return True
        elif await page.xpath('//img[@id="yodaImgCode"]'):
            self.logger.error('验证失败! ')
            return False

    @check_user()
    async def run(self, load_cookies: bool = True):
        if load_cookies:
            cookies = self.redis_client.load_cookies(self.site, self.username)
            if cookies:
                if self.check_islogin(cookies):
                    return True
                self.logger.info('cookies 已过期! ')

        await self.login()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(MeituanLogin().run(load_cookies=True))
