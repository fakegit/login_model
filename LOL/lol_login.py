import execjs
import requests
import re
from utils import *
from urllib.parse import urlencode
from cookies_pool import RedisClient

"""
腾讯 QQ 系登录( QQ 邮箱、 QQ 空间、 QQ 音乐 、 腾讯视频等)模拟登录流程都是一样的, 只需要改 ul、aid 等参数就可以了。
"""


class LOLLogin:

    def __init__(self, username: str = None, password: str = None):
        self.site = 'lol'
        self.username = username
        self.password = password
        self.logger = get_logger()
        self.redis_client = RedisClient(self.logger)
        self.session = requests.session()
        self.session.headers = {
            'Connection': 'keep-alive',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:68.0) Gecko/20100101 Firefox/68.0'
        }
        # 密码错误重置初始化
        self.reset_flag = False

        with open('encrypt.js', 'rb') as f:
            js = f.read().decode()
        self.ctx = execjs.compile(js)

    def check_islogin(self, cookies):
        params = {
            'use': 'zm,uid,acc',
            'area': '19',
            'season': 's9',
            'callback': 'jQuery191005632563829884707_{}'.format(int(time.time() * 1000)),
            '_': int(time.time() * 1000)
        }
        url = 'https://lol.ams.game.qq.com/lol/autocms/v1/transit/LOL/LOLWeb/Official/MobilePlayerInfo,PlayerCommunityInfo,PlayerInfo,PlayerBattleSummary,PlayerHonor,PlayerProperty,PlayerRankInfo?' + urlencode(params)
        res = self.session.get(url, cookies=cookies)
        result = json.loads(re.search(r'{}\((.*?)\)'.format(params['callback']), res.text).group(1))
        if result['MobilePlayerInfo']['status'] == 0:
            self.logger.info('Cookies 有效! ')
            nickname = result['MobilePlayerInfo']['msg']['res']['uuid_prifle_list'][0]['nick']
            self.logger.info('Hello, {}! '.format(nickname))
            gamename = result['PlayerInfo']['msg']['name']
            self.logger.info('你的游戏昵称: {}'.format(gamename))
            self.logger.info('查看战绩请按 1, 结束请按 0 >>')
            flag = int(input())
            if flag:
                seasons = result['PlayerBattleSummary']['msg']['data']['item_list']
                for season in seasons:
                    self.logger.info(season)
                return True
            return True
        return False

    def _init_cookies(self):
        self.session.get('https://mail.qq.com/')

    def _get_login_sig(self):
        res = self.session.get(
            'https://xui.ptlogin2.qq.com/cgi-bin/xlogin?proxy_url=https://game.qq.com/comm-htdocs/milo/proxy.html&appid=21000501&target=top&s_url=https%3A%2F%2Flol.qq.com%2Fmain.shtml&style=20&daid=8'
        )
        cookies = res.cookies.get_dict()
        login_sig = cookies['pt_login_sig']
        return cookies, login_sig

    def _get_salt(self, login_sig):
        url = 'https://ssl.ptlogin2.qq.com/check?'

        params = {
            'regmaster': '',
            'pt_tea': '2',
            'pt_vcode': '1',
            'uin': self.username,
            'appid': 21000501,
            'js_ver': '19072517',
            'js_type': 1,
            'login_sig': login_sig,
            'u1': 'https://lol.qq.com/main.shtml',
            'r': self.ctx.call('get_random_num'),
            'pt_uistyle': '40'
        }

        res = self.session.get(url, params=params)
        pt_verifysession_v1 = res.text.split(',')[3].replace("'", '')
        verify_code = res.text.split(',')[1].replace("'", '')
        salt = res.text.split(',')[2].replace("'", '')
        salt = salt.encode().decode('unicode_escape')
        ptdrvs = res.text.split(',')[5].replace("'", '').replace(')', '').strip()

        return pt_verifysession_v1, verify_code, salt, ptdrvs

    def _encrypt_pwd(self, salt, verify_code):
        return self.ctx.call('encrypt_pwd', self.password, salt, verify_code)

    @loopUnlessSeccessOrMaxTry(3, sleep_time=3)
    def login(self):
        self._init_cookies()
        login_api = 'https://ssl.ptlogin2.qq.com/login?'

        login_sig = self._get_login_sig()

        pt_verifysession_v1, verify_code, salt, ptdrvs = self._get_salt(login_sig)
        pwd = self._encrypt_pwd(salt, verify_code)

        params = {
            'u': self.username,
            'verifycode': verify_code,
            'pt_vcode_v1': '0',
            'pt_verifysession_v1': pt_verifysession_v1,
            'p': pwd,
            'pt_randsalt': '2',
            'u1': 'https://lol.qq.com/main.shtml',
            'ptredirect': '1',
            'h': '1',
            't': '1',
            'g': '1',
            'from_ui': '1',
            'ptlang': '2052',
            'action': f'1-0-{int(time.time() * 1000)}',
            'js_ver': '19072517',
            'js_type': '1',
            'login_sig': login_sig,
            'pt_uistyle': '40',
            'aid': 21000501,
            'daid': '8',
            'ptdrvs': ptdrvs,
            '': ''
        }

        res = self.session.get(login_api, params=params)
        result = re.search(r'ptuiCB\((.*?)\)', res.text).group(1).replace("'", '')
        result = result.split(',')

        if result[0] == '0':
            url = result[2]
            resp = self.session.get(url, allow_redirects=False)
            if resp.status_code == 302 and resp.headers['location'] == 'https://lol.qq.com/main.shtml':
                self.logger.info('登录成功! ')
                nickname = result[-1]
                self.logger.info('Hello, {}! '.format(nickname))
                cookies = resp.cookies.get_dict()
                self.redis_client.save_cookies(self.site, self.username, cookies)
                return cookies
            raise Exception('登录失败! ')
        elif '密码不正确' in result[-2]:
            self.reset_flag = True
            raise Exception('账号或密码错误! ')
        elif '二维码登录' in res.text:
            self.logger.warning('为了更好的保护您的QQ，请使用扫描二维码登录! ')
            return None
        raise Exception('登录失败: {} '.format(result[-2]))

    @check_user()
    def run(self, load_cookies: bool = True):

        if load_cookies:
            cookies = self.redis_client.load_cookies(self.site, self.username)
            if cookies:
                if self.check_islogin(cookies):
                    return cookies
                self.logger.warning('Cookies 已过期')

        self.login()


if __name__ == '__main__':
    x = LOLLogin().run(load_cookies=True)
    print(x)
