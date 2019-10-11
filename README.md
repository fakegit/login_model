# 网站模拟登录

目前实现站点:
-----------

   * 网易邮箱
   * 网易云音乐
   * 百度
   * B站
   * 博客园
   * 斗米
   * Github
   * 虎牙
   * 爱奇艺
   * 京东
   * 迅雷看看
   * 猎聘
   * 腾讯系(QQ)
   * 懒人听书
   * 美团
   * 咪咕音乐
   * 文书网
   * 企查查
   * 启信宝(需要极验3验证)
   * 人人网
   * 实习僧
   * stream
   * 淘宝
   * 今日头条
   * 微博
   * 喜马拉雅
   * YY 
   * 知乎
   * 智联
   * Boss 直聘

API 服务
------

 * 配置
    在 server.py 中导入站点登录类, 并在 WEBSITE_MAP 中添加站点登录类名即可
 * 运行
    python server.py

环境依赖
--------

* 使用 execjs 执行 js, 安装: pip install PyExecjs 。 
* python 复写的加密使用的包为 pycryptodemo, 安装: pip install pycryptodemo 。
* execjs 执行环境为 node.js。自行下载安装 node.js。
  注意: 安装完毕后, 使用 execjs.get().name 判断运行环境是否已成功切换为 'Node.js(V8)', 若未切换成功, 使用 os.environ["EXECJS_RUNTIME"] = "Node" 切换。
* 部分网站使用 selenium 或者 pyppeteer 登录, 安装最新版即可。 

注意
------

 * 超级鹰验证码服务请修改账号密码
 
公告
--------

该项目仅供学习参考, 请勿用作非法用途! 如若涉及侵权, 请联系2995438815@qq.com/18829040039@163.com, 收到必删除! 