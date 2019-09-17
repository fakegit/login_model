# -*- coding: UTF-8 -*-
# author: 许智海
# datetime:2019/6/12 18:08
# software: PyCharm

import execjs
import requests
import re
from utils import *
from pprint import pprint
from cookies_pool import RedisClient
import json
import time


class Email163Login:

    def __init__(self, username: str = None, password: str = None):
        self.site = '163email'
        self.username = username
        self.password = password
        self.logger = get_logger()
        self.redis_client = RedisClient(self.logger)
        self.session = requests.session()
        self.session.headers = {
            'Content-Type': 'application/json',
            'Origin': 'https://dl.reg.163.com',
            'Referer': 'https://dl.reg.163.com/webzj/v1.0.1/pub/index_dl2_new.html?cd=https%3A%2F%2Fmimg.127.net%2Fp%2Ffreemail%2Findex%2Funified%2Fstatic%2F2019%2Fcss%2F&cf=urs.163.bc0e7491.css&MGID=1561887066637.6414&wdaId=&pkid=CvViHzl&product=mail163',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.80 Safari/537.36',
        }
        with open('encryptEnvinfo.js', 'r') as f:
            self.js = f.read()
        self.ctx = execjs.compile(self.js)
        self.rtid = self.ctx.call('getRtid')

        # 密码错误重试初始化
        self.reset_flag = False

    def check_islogin(self, cookies):

        sid = cookies['sid']

        params = {
            'sid': sid
        }
        cookie = cookies['cookies']

        resp = self.session.get('http://mail.163.com/js6/main.jsp?', params=params, cookies=cookie)

        if '收件箱' in resp.text:
            self.logger.info('Cookies 有效! ')

            nickname = re.search("'true_name':'(.*?)'", resp.text).group(1)
            self.logger.info('Hello, {}! '.format(nickname))
            return True
        return False

    def _set_data(self, func):
        """
        配置收件箱接口表单参数
        :return:
        """
        with open('data.html', 'r') as f:
            html = f.read()
        data_list = html.split('<?xml version="1.0"?>')
        if func == 'global:sequential':
            return data_list[1]
        elif func == 'mbox:listMessages':
            return data_list[2]
        elif func == 'mbox:readMessage':
            return data_list[3]
        else:
            self.logger.warning('不支持的接口类型, 有需要请自行添加! ')

    @staticmethod
    def _format_date(text):
        """
        格式化日期
        :param date:
        :return:
        """
        date = re.search(r"new Date\((.*?)\)", text, re.S)
        send_time = '-'.join([x for x in date.group(1).split(',')[:3]]) + ' ' + ':'.join(
            [x for x in date.group(1).split(',')[3:]])
        return text.replace(date.group(0), send_time)

    def _read_email(self, cookies):
        """
        查看收件箱: 接口返回的数据是字典样式的原生字符串, demjson 格式化后都无法转为 json 格式... 懒得用正则提取了, 将就看
        :return:
        """
        cookie = cookies['cookies']
        sid = cookies['sid']
        self.session.headers.update({
            'Accept': 'text/javascript',  # 请求头携带这个参数接口返回的是格式化数据, 没有这个参数返回的html源码
            'Content-type': 'application/x-www-form-urlencoded'
        })
        url = 'https://mail.163.com/js6/s?'
        func_map = {
            '1': 'global:sequential',
            '2': 'mbox:listMessages',
            '3': 'mbox:readMessage'
        }
        sign_list = []
        all_flag = input('是否查看邮箱整体信息? (yes/任意键跳过) >> \n')
        if all_flag == 'yes':
            all_flag = 1
        else:
            all_flag = 0
        if all_flag:
            sign_list.append('1')
        mailbox_flag = input('是否查看收件箱邮件列表? (yes/任意键跳过) >> \n')
        if mailbox_flag == 'yes':
            mailbox_flag = 1
        else:
            mailbox_flag = 0
        if mailbox_flag:
            sign_list.append('2')
        for sign in sign_list:
            params = {
                'sid': sid,
                'func': func_map[sign],
            }
            data = {
                'var': self._set_data(func_map[sign])
            }
            res = self.session.post(url, params=params, data=data, cookies=cookie)
            if sign == '1':
                self.logger.info('邮箱整体信息如下:')
                pprint(res.text)
            elif sign == '2':
                self.logger.info('收件箱邮件列表: ')
                ids = re.findall("'id':'(.*?)'", res.text)
                subjects = re.findall("'subject':'(.*?)'", res.text)
                id_dict = {str(index): id_ for index, id_ in enumerate(ids)}
                subject_dict = {str(index): subject for index, subject in enumerate(subjects)}
                if id_dict:
                    pprint(subject_dict)
                    view_flag = input('是否需要查看具体邮件信息? (yes/任意键退出) >> \n')
                    if view_flag == 'yes':
                        view_flag = 1
                    else:
                        view_flag = 0
                    while view_flag:
                        email_num = input('请输入邮件编号(左边数字)>> ')
                        params = {
                            'sid': sid,
                            'func': func_map['3'],
                        }
                        origin_id = re.search('"id">(.*?)<', self._set_data(func_map['3'])).group(1)
                        data = {
                            'var': self._set_data(func_map['3']).replace(origin_id, id_dict[email_num])
                        }
                        resp = self.session.post(url, params=params, data=data, cookies=cookie)
                        result = self._format_date(resp.text)
                        pprint(result)
                        view_flag = int(input('继续查看请按 1 , 退出程序请按 0 >> \n'))
                else:
                    self.logger.info('收件箱列表空空如也~ ')

    def _init_cookies(self):
        """
        初始化 Cookies, 关键 Cookie: l_s_mail163CvViHzl, 有这个 Cookie 拿到 tk
        :return:
        """
        url = 'https://dl.reg.163.com/dl/ini?'
        params = {
            "pd": "mail163",
            "pkid": "CvViHzl",
            "pkht": "mail.163.com",
            "channel": "0",
            "topURL": "https://mail.163.com/",
            "rtid": self.rtid,
            "nocache": int(time.time() * 1000)
        }
        self.session.get(url, params=params)

    def _get_token(self):
        url = 'https://dl.reg.163.com/gt?'

        params = {
            'un': self.username,
            'pkid': 'CvViHzl',
            'pd': 'mail163',
            'channel': 0,
            'topURL': 'https://mail.163.com/',
            'rtid': self.rtid,
            'nocache': int(time.time() * 1000)
        }

        res = self.session.get(url, params=params).json()
        token = res['tk']
        return token

    def _encrypt_pwd(self):
        """
        加密密码
        :return:
        """
        return self.ctx.call('encrypt2', self.password)

    @loopUnlessSeccessOrMaxTry(3, sleep_time=3)
    def login(self):
        self._init_cookies()
        tk = self._get_token()

        login_api = 'https://dl.reg.163.com/dl/l'

        data = {
            "un": self.username,
            "pw": self._encrypt_pwd(),
            "pd": "mail163",
            "l": 0,
            "channel": 0,
            "d": 10,
            "t": int(time.time() * 1000),
            "pkid": "CvViHzl",
            "domains": "",
            "tk": tk,
            "pwdKeyUp": 1,
            "topURL": "https://mail.163.com/",
            "rtid": self.rtid
        }

        self.session.headers.update({'Cookie': 'JSESSIONID-WYTXZDL=YuenayJO3PfX%2BYyPmO%2Fhr%2FLeuu67nXDZPl50EOxAi9plAsq%5CKwf%5CZtQUUxOLA%2FxMlf%2FfxzPNLbTGxZaHUPTny%2BehaVqiukV7ed%2Fblp101N%2BGIIGYKZ9ODzLdR5w5eK%5ChGHO%2FFs2z4umi4Wj2xDzvxbm%2F8lTJBlIU6b9bF0FJrdn1%2Be%2Fq%3A1565361595090; l_s_mail163CvViHzl=2BDA1093FDDA9283AD02B57FFFEC7E0E75F576DC05D86CE6F6B6F9518A920CC1446CE99EF410B468FEDA27F8B53F2F93244D4991F985FACFD8D854C5298024A35F4A702F5D8A93285EB127782B2C254290B1202774ECFD0CE880601326AA4B229FF48A285C3118029255EAE3F260AA5A'})
        res = self.session.post(login_api, data=json.dumps(data)).json()

        if res['ret'] == '201':
            form_data = {
                "style": "-1", "df": "mail163_letter", "allssl": "true", "net": "", "language": "-1",
                "from": "web", "race": "", "iframe": "1",
                "url2": "https://mail.163.com/errorpage/error163.htm",
                "product": "mail163"
            }

            cookies = 'NTES_SESS=' + self.session.cookies.get_dict()['NTES_SESS']
            self.session.headers.update({'Cookie': cookies})
            resp = self.session.post('https://mail.163.com/entry/cgi/ntesdoor?', data=form_data, allow_redirects=False)
            redirect_url = resp.headers['location']

            if 'sid' in redirect_url:
                self.logger.info('登录成功! ')
                response = self.session.get(redirect_url)

                # 网易邮箱的关键是这个sid, 是session id 的意思, 有了它就可以爬邮箱了, 当然还要有配套的 Cookie
                cookies_item = {
                    'cookies': resp.cookies.get_dict(),
                    'sid': response.cookies.get_dict()['Coremail.sid']
                }
                self.redis_client.save_cookies(self.site, self.username, cookies_item)
                try:
                    nickname = re.search("'true_name':'(.*?)'", response.text).group(1)
                    self.logger.info('Hello, {}! '.format(nickname))
                except:
                    self.logger.info('你还没有设置昵称, 快去设置...')
                return True
            raise Exception('登录失败! ')
        elif res['ret'] == '413':
            self.reset_flag = True
            raise Exception('账号或密码错误! ')
        elif res['ret'] == '445':
            self.logger.warning('验证码校验...')
            return False
        elif res['ret'] == '409':
            self.logger.warning('登录过于频繁, 请稍后再试! ')
            return False
        elif res['ret'] == '423':
            self.logger.warning('风控账号! ')
            return False
        raise Exception('登录失败! ')

    @check_user()
    def run(self, load_cookies: bool = True):
        if '163.com' not in self.username:
            self.username += '@163.com'
        if load_cookies:
            cookies = self.redis_client.load_cookies(self.site, self.username)

            if cookies:
                if self.check_islogin(cookies):
                    read_flag = input('是否需要查看邮箱? (yes/任意键退出) >> \n')
                    if read_flag == 'yes':
                        self._read_email(cookies)
                    return True
                self.logger.warning('Cookies 已过期')

        self.login()


if __name__ == '__main__':
    Email163Login().run(load_cookies=True)
