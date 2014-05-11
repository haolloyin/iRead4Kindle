iRead.Kindle
============

A simple Django site for sharing Kindle highlights to Sina Weibo &amp; Douban broadcast(not yet supported).

## Introduction
----

iRead.Kindle is inspired by kindle.io (site: http://kindle.io/, source code: https://github.com/mitnk/kindleio), developed under Django-1.2.7 and host at SAE.

Now you can visit http://iread4kindle.sinaapp.com/ for sharing you Kindle highlights to Weibo. After you authorize to iRead.Kindle, it will fetch you latest Kindle highlights every 10 minutes and share to Weibo.


`Just sharing :)` from the author of kindle.io


iRead.Kindle is now an __incomplete__ service, there exists many terrible BUGs, the source code is ugly, howerver, `Done is better than perfect`, so I published it just for fun ;-)



## kindle.io 与 iRead4Kindle 抓取 Kindle highlights 的不同方法


------
### kindle.io 的功能

常读 Hacker News 的同学，肯定会认为 [kindle.io](http://kindle.io) 是个很不错的应用，它有三个功能（详看 [http://kindle.io/about/](http://kindle.io/about/)）：

- 给定网页 URL，将页面的 body 内容推送到你的 kindle
- 推送 Hacker News（http://news.ycombinator.com/）文章到你的 kindle
     + 每天：超过你指定的 points 数的文章将会被推送
     + 每周：points 数超过 200 的文章合集
- kindle.io 会 follow 与你 kindle 绑定的 Twitter 帐号，实时获取 timeline，以抓取你用 kindle share 出来的 highlights、notes，保存在 kindle.io 中（http://kindle.io/notes/）

kindle.io 基于 Django-1.4 开发，源码在 github：https://github.com/mitnk/kindleio


------
### iRead4Kindle

iRead4Kindle 是一个几乎完全山寨 kindle.io 的应用（已经和原作者邮件沟通过，他支持说「折腾东东学编程最快了」），照搬其页面设计，对功能代码有删有改，「降级」到基于 Django-1.2.7，托管在 SAE 试用（http://iread4kindle.sinaapp.com/），源码在 github：https://github.com/haolloyin/iRead4Kindle（由于 SAE 只支持 SVN 版本控制，故 github 上的可能跟 SAE 上试运行的有些微差异）。

iRead4Kindle 只有一个功能，抓取 kindle 用户的 highlights 并分享到新浪微博。在抓取 highlight 方面，iRead4Kindle 有如下步骤：

- 用户将自己的 Kindle Profile 页面的 URL 提供给 iRead4Kindle
     + 该页面是公开的，任何人都能访问，只是存放了你用 kindle share 出来的内容而已
     + 不需要你提供自己的 Twitter 账号
     + 登录 https://kindle.amazon.com/，鼠标移到右上角的「Hello，xxx」出现下拉框，点击「Your profile」进入 profile 页面，iRead4Kindle 需要的就是这个页面的 URL
     + iRead4Kindle 目前是每10分钟触发一个 Cron 任务，通过上述的 URL 抓取每个用户的 highlights，保存起来
     + 如果用户已经选择了「自动发布微博」，则 iRead4Kindle 会发布一条微博，内容包含本次抓取的结果到 iRead4Kindle 的链接（用于查看这些 highlights）
     + 如果不选择「自动发布微博」，则可以用 iRead4Kindle 手动触发发送一条微博


------
### 为啥做 iRead4Kindle

因为 kindle 的 Social Networks（https://kindle.amazon.com/home/preferences）只支持绑定 Twitter 和 Facebook 账号，kindle 用户可以将阅读过程中的 highlights、notes（类似于在书中划线、做笔记）分享到 Twitter 和 Facebook 和好友进行交流。

但是，由于某种神秘的原因，我们国内只能用微博，而且看到 SAE 提供了 Cron 定时服务，于是就做了 iRead4Kindle 抓取 kindle 用户的 highlights 分享到新浪微博。

遗憾的是，我们平时都用 kindle 读 Personal Documents，而不是读 Amazon 上原版的书籍，因此并不会将书名等信息保存到 Amazon，所以即使我们到 Kindle profile 页面也是看不到书名的。


------
### iRead4Kindle 的特点

- 优点

相比 kindle 官方绑定 Twitter 和 Facebook，iRead4Kindle 不会对你 kindle 的每一条 share 都自动发一条 推，而是至少每10分钟才发一次，减少微博发送太频繁。此外，你可以关闭「自动发布微博」的选项，用手动触发的方式抓取最新的 highlight 并发布一条微博。

另外一点，iRead4Kindle 不需要你提供 Twitter 和 Facebook 账号，尽管这两中账号在 share highlights、notes 时至少要绑定一个，似乎 kindle 只有通过这种 social network的方式将 highlights、notes 保存到 https://kindle.amazon.com 页面。绑定这两种帐号需要到 https://kindle.amazon.com/home/preferences 进行操作。

- 不足

由于 kindle profile 页面一打开只有10个条目，目前 iRead4Kindle 就只会傻傻地抓取这10个条目，一旦某个10分钟区间内你用 kindle share 超过10条，iRead4Kindle 将无法完全获取到，但是 kindle.io 可以做到这点，赞！

目前新浪微博的开发者身份还在申请当中，故每一个微博授权发布微博的 access token 有效期只是 24小时，过后就不能自动发布微博了。这个得等申请下来后再申请个永久性的 access token 的权限才能解决。

highlights 页面非常烂，右上角那个 hello，xxx 在给匿名用户访问时很不合理。about 页面的英文很水。整个应用的操作流程也模糊不清。代码更烂，这个毫无疑问的 :-(


------
### TODO

当然是要解决上面提出的不足。

当10分钟 share 超过10条之后，kindle profile 页面最底下有个「See More」按钮，看到其 URL 格式，发现多用了一个 offset=10 的偏移参数来获取另外10条。这个不足有办法来处理了，就差空点时间来搞搞了 ;-)


------
### 截图

- 包含单条 highlight 的微博，点击链接跳到 iRead4Kindle 的阅读页面

![包含单条 highlight 的微博，点击链接跳到 iRead4Kindle 的阅读页面](https://github.com/haolloyin/iRead4Kindle/blob/master/p214983241-1.jpg?raw=true)

- 从微博链接过来的单条 highlight

![从微博链接过来的单条 highlight](https://github.com/haolloyin/iRead4Kindle/blob/master/p214983241-2.jpg?raw=true)

- 包含多条 highlight 的微博

![包含多条 highlight 的微博](https://github.com/haolloyin/iRead4Kindle/blob/master/p214983241-3.jpg?raw=true)

- 从微博链接过来的多条 highlight

![从微博链接过来的多条 highlight](https://github.com/haolloyin/iRead4Kindle/blob/master/p214983241-4.jpg?raw=true)

- profile 页面，可以手动触发抓取最新 highlight 并发布微博

![profile 页面，可以手动触发抓取最新 highlight 并发布微博](https://github.com/haolloyin/iRead4Kindle/blob/master/p214983241-10.jpg?raw=true)

- profile 页面，填写 kindle profile URL，设置自动发布微博

![profile 页面，填写 kindle profile URL，设置自动发布微博](https://github.com/haolloyin/iRead4Kindle/blob/master/p214983241-11.jpg?raw=true)
