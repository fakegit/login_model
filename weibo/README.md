
微博登录
======================

破解微博su、sp加密参数，实现登录获取cookies

超详细破解流程
============================

篇幅有限, 这里只放了一部分图, 所有图在pic文件夹里。
---------------------------------
点击微博主页（https://weibo.com/） 的右上角的登录按钮
![image](https://github.com/Esbiya/login_model/blob/master/weibo/image/1.png)

然后F12进入开发者模式可以看到登录的API接口为https://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.19)  接一个时间戳。
![image](https://github.com/Esbiya/login_model/blob/master/weibo/image/4.png)
找到了接口之后，观察他的参数，看起来像加密参数的有pcid、door、su、nonce、pwencode、rsakv、sp, 其中servertime像时间戳。通过不同账号多次登录发现pwencode是固定参数, pcid、nonce、rsakv、servertime在另一个接口 https://login.sina.com.cn/sso/prelogin.php?  的response中发现(这个接口用到了su参数), door为输入的验证码, 接口为 https://login.sina.com.cn/cgi/pin.php?r=16343619&s=0&p={pcid} (用到了pcid参数), 所以我们的关键是先获取su参数, 然后利用su参数去获取其他的参数, 最后获取sp参数。

知道了我们要获取的所有参数及流程之后, 接下来就需要找到生成su参数的js代码, 这里我们不尝试直接全局搜索su, 因为su太短, 很容易匹配到很多无关文件, 那怎么办呢？（1）: 用其他的固定参数尝试去搜索; （2）: 将这个XHR请求加入断点。尝试之后采用第二种方法。

添加XHR断点: 点击图中箭头所指的加号, 将https://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.19)添加进去, 然后重新输入登陆。
![image](https://github.com/Esbiya/login_model/blob/master/weibo/image/5.png)

这时开发者工具会自动弹出来, 页面停止在断点处, 观察开发者工具中source部分断点处代码, 发现所有参数的生成方法都在里面。
![image](https://github.com/Esbiya/login_model/blob/master/weibo/image/6.png)

往上滑一点, 发现关键的参数中, su和sp的生成方法都在, 可以看出sr参数为屏幕的尺寸。
![image](https://github.com/Esbiya/login_model/blob/master/weibo/image/7.png)

这时候我们需要找出所有生成函数需要用到的方法, 我们将鼠标移至生成函数的方法上即可看见实际函数, 然后点击跳转即可, 如下图。
![image](https://github.com/Esbiya/login_model/blob/master/weibo/image/8.png)

可能会出现部分方法显示undefined, 如果出现这种情况, 请先点击下图中第一个按钮释放掉断点。
![image](https://github.com/Esbiya/login_model/blob/master/weibo/image/20.png)

然后在该处设置断点重新登录, 即可看见所有方法。
![image](https://github.com/Esbiya/login_model/blob/master/weibo/image/11.png)

还需要知道生成函数用到了哪些参数, 也是同样的方法, 将鼠标移至参数上即可看见参数的值, 可以看出su生成函数用到的参数a为你的电话号码, sp生成参数用到的me.rsaPubkey, me.servertime、me.nonce为上一个接口获取的pubkey、servertime、nonce, b为你的密码。从这里可以看出密码加密用到了RSA加密。
![image](https://github.com/Esbiya/login_model/blob/master/weibo/image/14.png)

点击方法跳转进入生成su生成函数, 是这个样子的：
![image](https://github.com/Esbiya/login_model/blob/master/weibo/image/15.png)
![image](https://github.com/Esbiya/login_model/blob/master/weibo/image/17.png)
可以看见电话号码的加密就是这个base64函数的encode方法(嗯其实一开始看见su参数的样子时, 发现它尾巴上的"="号, 就应该猜想它经过了base64编码加密, 这是一个很重要的经验), 直接copy出去到控制台运行之后报错缺少上图小框中的参数。

然后我们需要寻找这些参数的生成方法或者值, 直接复制然后搜索, 发现所有餐所均为定值:
![image](https://github.com/Esbiya/login_model/blob/master/weibo/image/16.png)

copy出去稍微改一下, 在控制台运行一下, 果然su参数出来了, 对比请求中的su参数, 发现完全正确。完成第一步, su参数生成比较简单。
![image](https://github.com/Esbiya/login_model/blob/master/weibo/image/21.png)

接下来就是利用生成的su参数请求我们找到的接口获取pubkey密钥、验证码等参数, 然后寻找sp生成函数。点击方法进入:
![image](https://github.com/Esbiya/login_model/blob/master/weibo/image/18.png)
可以看见很多相似的函数名, 遇到这种情况, 应该是用到了一整个大函数(经验), 试着将一整个大函数都copy下来,截止到下图:
![image](https://github.com/Esbiya/login_model/blob/master/weibo/image/19.png)

然后写一个主生成函数放入控制台运行, 报错sinaSSOEncoder.rsaPubkey不是一个constructor, 这里应该是用到js原形, 不是很懂(我的js稀烂)。改了半天, 添加window对象定义, 运行结果:
![image](https://github.com/Esbiya/login_model/blob/master/weibo/image/22.png)

好了, 至此所有的参数都出来了, 请求接口即可。

公告
========================
仅供学习交流, 请勿用做商业用途, 否则后果自负！
