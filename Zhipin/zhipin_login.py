# -*- coding: utf-8 -*-
# @Time    : 2019/7/28 23:00
# @Author  : xuzhihai0723
# @Email   : 18829040039@163.com
# @File    : zhipin_login.py
# @Software: PyCharm

import asyncio
import re
import requests
import random
from utils import *
from cookies_pool import RedisClient
from pyppeteer.launcher import launch


class ZhipinLogin:

    def __init__(self, username: str = None, password: str = None):
        self.site = 'zhipin'
        self.logger = get_logger()
        self.username = username
        self.password = password
        self.redis_client = RedisClient(self.logger)

    async def check_islogin(self, cookies):
        """
        检查登录状态: 访问首页, 出现用户名则登录成功
        :param page:
        :return:
        """

        url = 'https://www.zhipin.com/geek/new/index/recommend?ka=header-personal'

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 Edge/16.16299'
        }

        res = requests.get(url, headers=headers, cookies=cookies)

        if '登录' not in res.text:
            self.logger.info('Cookies 有效! ')
            nickname = re.search('name:"(.*?)"', res.text).group(1)
            self.logger.info('Hello, {}! '.format(nickname))
            return True
        return False

    @staticmethod
    def input_time_random():
        return random.randint(150, 201)

    def retry_if_result_none(self, result):
        self.logger.warning('滑块判定失败, 重试！')
        return result is None

    async def login(self):

        browser = await launch(
            {
                'headless': False,
                'args': ['--no-sandbox', '--disable-infobars'],
            },
            # userDataDir=r'D:\login\userdata',   # 这个文件会记录pyppeteer浏览器的cookie
            args=['--window-size=1366, 768']
        )
        page = await browser.newPage()  # 启动个新的浏览器页面
        await page.setJavaScriptEnabled(enabled=True)  # 启用js
        await page.setUserAgent(
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 Edge/16.16299'
        )  # 设置模拟浏览器

        self.logger.info('尝试登录...')

        await page.goto('https://www.zhipin.com/user/login.html')
        await self.page_evaluate(page)

        time.sleep(2)

        time.sleep(1)
        await page.type('input[name="account"]', self.username, {'delay': self.input_time_random() - 50})
        time.sleep(1)
        await page.type('input[name="password"]', self.password, {'delay': self.input_time_random()})

        # await page.screenshot({'path': './headless-test-result.png'})   # 截图测试
        time.sleep(2)

        self.logger.info('拉动滑块验证...')
        # await page.screenshot({'path': './headless-login-slide.png'})   # 截图测试
        flag = await self.mouse_slide(page=page)  # js拉动滑块
        if flag:
            # await page.keyboard.press('Enter')
            await page.click('button.btn')
            await page.waitFor(20)
            await page.waitForNavigation()  # 等待跳转
            try:
                global error
                error = await page.Jeval('.dialog-con', 'node => node.textContent')  # 检测是否是账号密码错误
            except Exception as e:
                error = None
                self.logger.info("登录成功! ")
            finally:
                if error:
                    error = await (await (await page.xpath('//div[@class="dialog-con"]'))[0].getProperty('textContent')).jsonValue()
                    self.logger.info(error)
                else:
                    await asyncio.sleep(3)
                    cookies = await page.cookies()
                    # cookies = {item['name']: item['value'] for item in cookies}
                    self.redis_client.save_cookies(self.site, self.username, cookies)
        else:
            self.logger.error('验证失败! ')

        await self.page_close(browser)

    async def page_evaluate(self, page):

        await page.evaluate(
            '''() =>{ Object.defineProperties(navigator,{ webdriver:{ get: () => undefined } }) }''')  # 以下为插入中间js，将淘宝会为了检测浏览器而调用的js修改其结果。
        await page.evaluate('''() =>{ window.navigator.chrome = { runtime: {},  }; }''')
        await page.evaluate(
            '''() =>{ Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] }); }''')
        await page.evaluate(
            '''() =>{ Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5,6], }); }''')

    async def page_close(self, browser):
        """
        关闭浏览器驱动
        :param browser:
        :return:
        """
        for _page in await browser.pages():
            await _page.close()
        await browser.close()

    # @retry(retry_on_result=retry_if_result_none, )
    async def mouse_slide(self, page=None):
        await asyncio.sleep(3)
        try:
            # 鼠标移动到滑块，按下，滑动到头（然后延时处理），松开按键
            await page.hover('.btn_slide')
            await page.mouse.down()  # 模拟按下鼠标
            await page.mouse.move(2000, 0, {'delay': random.randint(1000, 2000)})  # js模拟拖动
            await page.mouse.up()  # 模拟松开鼠标
        except Exception as e:
            return None, page
        else:
            await asyncio.sleep(2)
            slider_again = await page.Jeval('.nc-lang-cnt', 'node => node.textContent')  # 判断是否通过
            if slider_again != '验证通过':
                return None, page
            else:
                # await page.screenshot({'path': './headless-slide-result.png'}) # 截图测试
                self.logger.info('验证通过! ')
                return 1, page

    @check_user()
    async def run(self, load_cookies: bool = True):
        if load_cookies:
            cookies = self.redis_client.load_cookies(self.site, self.username)
            cookies = {item['name']: item['value'] for item in cookies}
            if cookies:
                if await self.check_islogin(cookies):
                    return True
                self.logger.warning('cookies 已过期! ')

        await self.login()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(ZhipinLogin().run(load_cookies=True))
