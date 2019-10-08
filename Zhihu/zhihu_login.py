# -*- coding: utf-8 -*-
# @Time    : 2019/7/2 12:35
# @Author  : Esbiya
# @Email   : 18829040039@163.com
# @File    : zhihu_login.py
# @Software: PyCharm

import re
import base64
import execjs
from chaojiying import image_to_text
import requests
import getpass
from utils import *
from http import cookiejar
from urllib.parse import urlencode
from cookies_pool import RedisClient


class ZhihuLogin:

    def __init__(self, username: str = None, password: str = None):
        self.site = 'zhihu'
        self.logger = get_logger()
        self.username = username
        self.password = password
        self.redis_client = RedisClient(self.logger)
        self.login_data = {
            'captcha': '',
            'client_id': 'c3cef7c66a1843f8b3a9e6a1e3160e20',
            'grant_type': 'password',
            'lang': 'en',
            'password': '',
            'ref_source': 'homepage',
            'signature': '',
            'source': 'com.zhihu.web',
            'timestamp': '',
            'username': '',
            'utm_source': ''
        }
        self.session = requests.session()
        self.session.headers = {
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-CN,zh;q=0.9',
            'origin': 'www.zhihu.com',
            'referer': 'https://www.zhihu.com/signin?next=%2F',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                          '(KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'
        }
        # 密码错误重置初始化
        self.reset_flag = False

    def check_islogin(self, cookies):
        """
        检查登录状态，访问登录页面跳转至首页则是已登录，
        如登录成功保存当前 Cookies
        :return: bool
        """
        login_url = 'https://www.zhihu.com/api/v4/me?include=ad_type%2Cavailable_message_types%2Cdefault_notifications_count%2Cfollow_notifications_count%2Cvote_thank_notifications_count%2Cmessages_count%2Caccount_status%2Cemail%2Cis_bind_phone'
        resp = self.session.get(login_url, cookies=cookies)
        if 'error' not in resp.text:
            self.logger.info('登录成功! ')
            nickname = resp.json()['name']
            self.logger.info('Hello, {}! '.format(nickname))
            return True
        return False

    @loopUnlessSeccessOrMaxTry(3, sleep_time=3)
    def _get_xsrf(self):
        """
        从登录页面获取 xsrf
        :return: str
        """
        self.session.get('https://www.zhihu.com/', allow_redirects=False)
        for cookie in self.session.cookies:
            if cookie.name == '_xsrf':
                # print(cookie.value)
                return cookie.value
        raise AssertionError('获取 xsrf 失败')

    @loopUnlessSeccessOrMaxTry(3, sleep_time=3)
    def _get_captcha(self, lang: str):
        """
        请求验证码的 API 接口，无论是否需要验证码都需要请求一次
        如果需要验证码会返回图片的 base64 编码
        根据 lang 参数匹配验证码
        :param lang: 返回验证码的语言(en/cn)
        :return: 验证码的 POST 参数
        """
        api = 'https://www.zhihu.com/api/v3/oauth/captcha?lang={}'.format(lang)
        resp = self.session.get(api)
        show_captcha = re.search(r'true', resp.text)

        if show_captcha:
            put_resp = self.session.put(api)
            json_data = json.loads(put_resp.text)
            img_base64 = json_data['img_base64'].replace(r'\n', '')
            img_data = base64.b64decode(img_base64)
            self.logger.info('使用超级鹰识别验证码...')
            ok, result = image_to_text(img_data)
            if ok:
                self.logger.info('成功识别验证码! ')
                # 这里必须先把参数 POST 验证码接口
                time.sleep(1)
                res = self.session.post(api, data={'input_text': result}).json()
                if 'success' in res.keys():
                    return result
                raise Exception('验证码 post 失败: {}'.format(res['error']['message']))
            raise Exception('验证码识别失败: ', result)
        raise Exception('获取验证码失败! ')

    @staticmethod
    def _get_signature(timestamp: int or str):
        """
        获取signature签名参数
        :param timestamp: 时间戳
        :return: 签名
        """
        with open('signature.js', 'rb') as f:
            js = f.read().decode()
        ctx = execjs.compile(js)
        signature = ctx.call('get_signature', timestamp)
        return signature

        # 直接用python内置Hmac加密算法如下,
        # def _get_signature(self, timestamp: int or str):
        #     """
        #     通过 Hmac 算法计算返回签名
        #     实际是几个固定字符串加时间戳
        #     :param timestamp: 时间戳
        #     :return: 签名
        #     """
        #     hmac = hmac.new(b'd1b964811afb40118a12068ff74a12f4', digestmod=hashlib.sha1)
        #     hmac.update(self.login_data['grant_type'].encode())
        #     hmac.update(self.login_data['client_id'].encode())
        #     hmac.update(self.login_data['source'].encode())
        #     hmac.update(str(timestamp).encode())
        #     signature = hmac.hexdigest()
        #     # print(signature)
        #     return signature

    @staticmethod
    def _encrypt(form_data):
        with open('get_formdata.js', 'rb') as f:
            js = f.read().decode()
        ctx = execjs.compile(js)
        data = ctx.call('encrypt', urlencode(form_data))
        # print('加密后的data: ', data)
        return data

    @loopUnlessSeccessOrMaxTry(3, sleep_time=3)
    def login(self, captcha_lang: str = 'en'):
        """
        模拟登录知乎
        :param captcha_lang: 验证码类型 'en' or 'cn'
        :return: bool
        若在 PyCharm 下使用中文验证出现无法点击的问题，
        需要在 Settings / Tools / Python Scientific / Show Plots in Toolwindow，取消勾选
        """

        self.login_data.update({
            'username': self.username,
            'password': self.password,
            'lang': captcha_lang
        })

        timestamp = int(time.time() * 1000)
        self.login_data.update({
            'captcha': self._get_captcha(self.login_data['lang']),
            'timestamp': timestamp,
            'signature': self._get_signature(timestamp)
        })
        headers = self.session.headers.copy()
        headers.update({
            'content-type': 'application/x-www-form-urlencoded',
            'x-zse-83': '3_2.0',
            'x-xsrftoken': self._get_xsrf(),
            'x-requested-with': 'fetch',
            'x-ab-param': 'se_time_threshold=0;zr_album_chapter_exp=0;li_price_test=1;li_qa_cover=old;se_ltr_v008=0;top_ebook=0;tp_qa_metacard=1;top_vipconsume=1;tp_header_style=1;li_album_liutongab=0;li_qa_new_cover=0;se_famous=1;se_search_feed=N;zr_album_exp=0;zr_km_xgb_model=old;ls_fmp4=1;se_colorfultab=1;se_limit=0;tp_qa_toast=1;top_reason=1;se_college=default;se_payconsult_click=0;se_topicdirect=2;se_zu_onebox=0;pf_feed=1;se_ri=0;top_test_4_liguangyi=1;tp_qa_metacard_top=top;li_album3_ab=0;qa_test=0;se_college_cm=0;se_title_only=0;top_rank=0;tp_sft=a;tp_sft_v2= a;ug_zero_follow_0=0;se_backsearch=0;se_bl=0;se_page_limit_20=1;se_rr=0;soc_bigone=0;ug_follow_topic_1=2;zr_infinity_a_u=close;li_auif_ab=0;pf_fuceng=1;se_mobileweb=0;se_websearch=3;li_se_ebook_chapter=1;se_payconsult=0;se_subtext=0;se_wannasearch=0;qa_answerlist_ad=0;se_auto_syn=0;top_root=0;se_featured=1;soc_special=0;tsp_hotctr=1;li_ebook_detail=1;ug_zero_follow=0;zr_art_rec=base;zr_video_recall=current_recall;top_recall_exp_v1=1;pf_noti_entry_num=0;se_site_onebox=0;se_time_score=1;top_quality=0;pf_foltopic_usernum=50;se_billboardsearch=0;zr_km_answer=open_cvr;se_ios_spb309=0;se_lottery=0;se_terminate=0;top_recall_deep_user=1;ls_videoad=0;se_webrs=1;tp_m_intro_re_topic=1;zr_km_style=base;ug_follow_answerer=0;top_hotcommerce=1;top_new_feed=5;pf_newguide_vertical=0;zr_ans_rec=gbrank;li_tjys_ec_ab=0;se_spb309=0;se_whitelist=0;se_amovietab=0;top_native_answer=1;top_recall_exp_v2=1;ug_goodcomment_0=1;pf_creator_card=1;se_ad_index=10;ug_follow_answerer_0=0;ug_goodcomment=0;se_topic_pu=0;se_webtimebox=0;tp_meta_card=0;tsp_childbillboard=1;se_expired_ob=0;se_new_topic=0;se_pay_score=0;se_p_slideshow=0;zr_rel_search=base;zr_video_rank=current_rank;top_gr_ab=0;tp_sticky_android=0;tsp_lastread=0;ug_newtag=0;li_hot_score_ab=0;se_movietab=0;se_pyc_click2=1;soc_bignew=1;zr_ebook_chapter=0;zr_km_slot_style=event_card;ls_new_upload=0;se_preset_tech=0;ug_fw_answ_aut_1=0;top_universalebook=1;top_ydyq=X;li_mceb=0;li_ts_sample=old;se_agency= 0;se_waterfall=0;se_timebox_num=3;se_topic_express=0;se_zu_recommend=0;zr_se_footer=1;se_likebutton=0;se_webmajorob=0;soc_update=1;zr_infinity_xgb=top3;se_ltr_v002=1;top_v_album=1;zr_es_update=0',
        })

        # 知乎的登录表单是加密后字符串作为键, 然后值为空的一个字典, 而不是直接用加密的字符串作为表单提交
        data = {self._encrypt(self.login_data): ''}
        login_api = 'https://www.zhihu.com/api/v3/oauth/sign_in'
        resp = self.session.post(login_api, data=data, headers=headers)
        cookies = resp.cookies.get_dict()
        if self.check_islogin(cookies):
            return cookies
        elif resp.json()['error']['message'] == '帐号或密码错误' or resp.json()['error']['message'] == '密码长度不足':
            self.reset_flag = True
            raise Exception('帐号或密码错误! ')
        raise Exception('登录失败: ', resp.json()['error']['message'])

    @check_user()
    def run(self, load_cookies: bool = True):
        if self.username.isdigit() and '+86' not in self.username:
            self.username = '+86' + self.username
        if load_cookies:
            cookies = self.redis_client.load_cookies(self.site, self.username)
            if cookies:
                if self.check_islogin(cookies):
                    return cookies
                self.logger.warning('Cookies 已过期')

        return self.login()


if __name__ == '__main__':
    x = ZhihuLogin().run(load_cookies=False)
    print(x)
