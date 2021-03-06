
from django.conf.urls.defaults import *

urlpatterns = patterns('iRead4Kindle.accounts.views',
    url(r'^login/$', 'site_login', name='accounts_login'),
    url(r'^signup/$', 'signup', name='accounts_signup'),
    url(r'^password_reset/$', 'password_reset', name='accounts_password_reset'),
    url(r'^logout/$', 'site_logout', name='accounts_logout'),
    url(r'^profile/$', 'profile', name='accounts_profile'),

    # login or oauth with douban

    url(r'^login_with_douban/$', 'douban_oauth', {'oauth_type': 'login'}, name="login_with_douban"),
    url(r'^oauth_with_douban/$', 'douban_oauth', {'oauth_type': 'oauth'}, name='oauth_with_douban'),
    url(r'^douban_callback/$', 'douban_callback', name="douban_callback"),

    # login or oauth with weibo
    url(r'^login_with_weibo/$', 'weibo_oauth', {'oauth_type': 'login'}, name="login_with_weibo"),
    url(r'^oauth_with_weibo/$', 'weibo_oauth', {'oauth_type': 'oauth'}, name='oauth_with_weibo'),
    url(r'^weibo_callback/$', 'weibo_callback', name="weibo_callback"),

)
