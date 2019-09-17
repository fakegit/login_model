# -*- coding: utf-8 -*-
# @Time    : 2019/7/28 9:18
# @Author  : Esbiya
# @Email   : 18829040039@163.com
# @File    : taobao_login.py
# @Software: PyCharm

import asyncio
import time
import random
from utils import *
from retrying import retry
from bs4 import BeautifulSoup
from cookies_pool import RedisClient
from pyppeteer.launcher import launch


class TaobaoLogin:

    def __init__(self, username: str = None, password: str = None):
        self.site = 'taobao'
        self.logger = get_logger()
        self.username = username
        self.password = password
        self.redis_client = RedisClient(self.logger)

    async def check_islogin(self, page):
        """
        检查登录状态: 访问首页, 出现用户名则登录成功
        :param page:
        :return:
        """

        await page.goto('https://www.taobao.com/')

        time.sleep(3)

        html = await page.content()

        bsobj = BeautifulSoup(html, 'lxml')

        if bsobj.find('a', {'class': 'site-nav-login-info-nick'}):
            self.logger.info('Cookies 有效! ')
            nickname = bsobj.find('a', {'class': 'site-nav-login-info-nick'}).get_text()
            self.logger.info('Hello, {}! '.format(nickname))
            cookies = await page.cookies()
            # cookies = {item['name']: item['value'] for item in cookies}
            self.redis_client.save_cookies(self.site, self.username, cookies)
            return True
        return False

    @staticmethod
    def input_time_random():
        return random.randint(150, 201)

    def retry_if_result_none(self, result):
        self.logger.warning('滑块判定失败, 重试！')
        return result is None

    @check_user()
    async def login(self):
        # 以下使用await 可以针对耗时的操作进行挂起
        # 记：一定要给pyppeteer权限删除用户数据, 即设置userDataDir: 文件夹名称, 否则会报错无法移除用户数据
        browser = await launch(
            {
                'headless': True,
                'args': ['--no-sandbox', '--disable-infobars'],
            },
            # userDataDir=r'D:\login\userdata',
            args=['--window-size=1366, 768']
        )
        page = await browser.newPage()  # 启动个新的浏览器页面
        await page.setJavaScriptEnabled(enabled=True)  # 启用js
        await page.setUserAgent(
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 Edge/16.16299'
        )  # 设置模拟浏览器

        self.logger.info('尝试登录...')

        await page.goto(
            'https://login.taobao.com/member/login.jhtml?spm=a21bo.2017.754894437.1.5af911d9qqVAb1&f=top&redirectURL=https%3A%2F%2Fwww.taobao.com%2F'
        )
        await self.page_evaluate(page)  # 修改window.navigator.webdriver = False, 这是绕过淘宝自动化工具检测的关键

        # 使用type选定页面元素，并修改其数值，用于输入账号密码，修改的速度仿人类操作，因为有个输入速度的检测机制
        # 因为 pyppeteer 框架需要转换为js操作，而js和python的类型定义不同，所以写法与参数要用字典，类型导入

        try:
            await page.click('#J_Quick2Static')   # 点击选择密码登录, 看你进入登录页面是否已经是密码登录, 若不是则需要点击选择密码登录
        except:
            pass

        time.sleep(1)

        # 清空用户名输入框, 确保正确输入: 用户名不为空时页面才会有清空节点 nickx
        try:
            await page.click('.nickx')
        except:
            pass

        # await page.evaluate('''() => { document.getElementById(TPL_username_1).value="" }''')
        time.sleep(1)
        await page.type('#TPL_username_1', self.username, {'delay': self.input_time_random() - 50})
        time.sleep(1)
        await page.type('#TPL_password_1', self.password, {'delay': self.input_time_random()})

        # await page.screenshot({'path': './headless-test-result.png'})   # 截图测试
        time.sleep(2)

        slider = await page.Jeval('#nocaptcha', 'node => node.style')  # 是否有滑块

        self.logger.info('账号密码输入完成, 判断滑块是否出现')
        if slider:
            self.logger.info('出现滑块情况判定')
            # await page.screenshot({'path': './headless-login-slide.png'})   # 截图测试
            flag = await self.mouse_slide(page=page)  # js拉动滑块
            if flag:
                # await page.keyboard.press('Enter')  # 模拟按键Enter确定 或鼠标点击登录
                await page.click('#J_SubmitStatic')
                time.sleep(1)
                cookies = await page.cookies()
                # cookies = {item['name']: item['value'] for item in cookies}
                self.redis_client.save_cookies(self.site, self.username, cookies)
        else:
            # await page.keyboard.press('Enter')
            self.logger.info('滑块未出现, 点击登录按钮')
            await page.click('#J_SubmitStatic')
            await page.waitFor(20)
            await page.waitForNavigation()  # 等待跳转
            try:
                global error
                error = await page.Jeval('.error', 'node => node.textContent')  # 检测是否是账号密码错误
            except Exception as e:
                error = None
                self.logger.info("登录成功! ")
            finally:
                if error:
                    # self.logger.info('确保账户安全重新输入')
                    error = await (await (await page.xpath('//div[@class="dialog-con"]'))[0].getProperty(
                        'textContent')).jsonValue()
                    self.logger.info(error)
                else:
                    await asyncio.sleep(3)
                    cookies = await page.cookies()
                    # print({item['name']: item['value'] for item in cookies})
                    self.redis_client.save_cookies(self.site, self.username, cookies)
        await self.page_close(browser)

    async def page_evaluate(self, page):
        # 替换淘宝在检测浏览时采集的一些参数。
        # 就是在浏览器运行的时候，始终让window.navigator.webdriver=false
        # navigator是windiw对象的一个属性，同时修改plugins，languages，navigator
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

    @retry(retry_on_result=retry_if_result_none, )
    async def mouse_slide(self, page=None):
        await asyncio.sleep(2)
        try:
            # 鼠标移动到滑块，按下，滑动到头（然后延时处理），松开按键
            await page.hover('#nc_1_n1z')  # 不同场景的验证码模块可能名字不同。
            await page.mouse.down()  # 模拟按下鼠标
            await page.mouse.move(2000, 0, {'delay': random.randint(1000, 2000)})  # js模拟拖动
            await page.mouse.up()  # 模拟松开鼠标
        except Exception as e:
            self.logger.error('验证失败: {}'.format(e.args))
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

    async def run(self, load_cookies: bool = True):
        if load_cookies:
            cookies = self.redis_client.load_cookies(self.site, self.username)
            if cookies:
                browser = await launch(
                    {
                        'headless': True,
                        'args': ['--no-sandbox', '--disable-infobars'],
                    },
                    userDataDir=r'D:\login\userdata',
                    args=['--window-size=1366, 768']
                )
                page = await browser.newPage()
                self.logger.info('将 cookies 装载到浏览器中...')
                await page.deleteCookie()
                for cookie in cookies:
                    await page.setCookie(cookie)
                if await self.check_islogin(page):
                    await self.page_close(browser)
                    return True
                await self.page_close(browser)
                self.logger.warning('cookies 已过期! ')

        await self.login()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(TaobaoLogin().run(load_cookies=True))
