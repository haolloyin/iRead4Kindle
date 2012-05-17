# coding=utf8


"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from urllib2 import urlopen
from bs4 import BeautifulSoup as BS

from django.contrib.auth.models import User

from iRead4Kindle.accounts.models import UserProfile
from iRead4Kindle.highlights.models import Highlight
from iRead4Kindle.accounts import utils as social_api

def fetch_all_hl(profile_url='', offset=0, new_urls=[], new_hls=[]):
    '''
from iRead4Kindle.highlights.tests import fetch_all_hl
urls, hls = [], []
fetch_all_hl(profile_url='hao/2585443', offset=0, new_urls=urls, new_hls=hls)
    '''
    assert new_hls != None
    assert new_urls != None
    p_url = 'https://kindle.amazon.com/profile/%s' % profile_url
    if offset != 0:
        p_url += '?offset=%s' % str(offset)
    page = urlopen(p_url)
    if page.getcode() != 200:
        print 'http error: ', page.getcode()
        return

    soup = BS(page, from_encoding='utf8')
    
    def _get_shared_tags(tag):
        return tag.has_key('href') and tag['href'].startswith('/post/')

    shared_posts = soup.find_all(_get_shared_tags)
    assert shared_posts != None
    posts = []
    urls = []
    count = 0
    for hl in shared_posts:
        count += 1
        hl_url = hl['href']
        posts.append(hl)
        urls.append(hl_url)

    new_hls.extend([share.find_next('div', {'class': 'sampleHighlight'}) \
            for share in posts])
    new_urls.extend(urls)

    print new_hls
    print new_urls

    print 'urls %s' % len(new_urls)
    print 'hls %s' % len(new_hls)

    if count == len(shared_posts):
        print 'fetched ', len(shared_posts)
        fetch_all_hl(profile_url, offset=offset+10, new_urls=new_urls, new_hls=new_hls)

    return (new_urls[::-1], new_hls[::-1])



def get_weibo_api(username='admin'):
    user = User.objects.get(username=username)
    up = UserProfile.objects.get(user=user)
    tokens = up.get_weibo_tokens_dict()
    api = social_api.get_weibo_api(up.weibo_id, token_dict=tokens)
    print 'weibo api is ok.'
    return api


def test_update_weibo():
    user = User.objects.get(username='admin')
    up = UserProfile.objects.get(user=user)
    tokens = up.get_weibo_tokens_dict()
    print tokens
    api = social_api.get_weibo_api(up.weibo_id, token_dict=tokens)
    text = u"""#iRead4Kindle#\u300c\n\n\u8d22\u5bcc\u548c\u7279\u6743\u5982\u4e3a\u5171\u540c\u6240\u6709\uff0c\u5219\u6700\u5bb9\u6613\u4fdd\u536b\u3002\u5728\u672c\u4e16\u7eaa\u4e2d\u53f6\u51fa\u73b0\u7684\u6240\u8c13\u201c\u53d6\u6d88\u79c1\u6709\u5236\u201d\uff0c\u5b9e\u9645\u4e0a\u610f\u5473\u7740\u628a\u8d22\u4ea7\u96c6\u4e2d\u5230\u6bd4\u4ee5\u524d\u66f4\u5c11\u5f97\u591a\u7684\u4e00\u6279\u4eba\u624b\u4e2d...\u300dhttp://127.0.0.1:8001/highlights/detail/4PDJX6UFZVWT/"""
    text = '测试发送中文微博'
    print text
    result = api.post.statuses__update(status=text)
    #result = api.get.statuses__user_timeline()
    print result

def test_weibo():
    for up in UserProfile.objects.all():
        test_weibo_api(up)
"""
(django-1.2.7-env)ihao-MacBook:iRead4Kindle mb375$ pym shell
>>> from iRead4Kindle.highlights import tests
>>> tests.test_weibo()
user_timeline: 
{'statuses': [u'3443177329761824', u'3443159214517418', u'3443019771009330', u'3442453233371151', u'3442452415779808', u'3442088698262246', u'3442088283155424', u'3441734128578805', u'3441361716061343', u'3441308821620931', u'3441242472346965', u'3441240073241144', u'3441239699288509', u'3441008279100633', u'3441007121583344', u'3441005716107076', u'3441003896071525', u'3440997373819592', u'3440995691906322', u'3440992592372201'], 'previous_cursor': 0, 'hasvisible': False, 'next_cursor': 0, 'total_number': 1763}
user_timeline: 
{'statuses': [u'3443177329761824', u'3443159214517418', u'3443019771009330', u'3442453233371151', u'3442452415779808', u'3442088698262246', u'3442088283155424', u'3441734128578805', u'3441361716061343', u'3441308821620931', u'3441242472346965', u'3441240073241144', u'3441239699288509', u'3441008279100633', u'3441007121583344', u'3441005716107076', u'3441003896071525', u'3440997373819592', u'3440995691906322', u'3440992592372201'], 'previous_cursor': 0, 'hasvisible': False, 'next_cursor': 0, 'total_number': 1763}
"""


def test_weibo_api(up):
    if up.has_weibo_oauth():
        weibo_tokens = up.get_weibo_tokens_dict()
        weibo_api = social_api._get_weibo_api(up.weibo_id, \
                weibo_tokens['access_token'], weibo_tokens['expires_in'])
        # new_status = u'%s' % ''
        # weibo_api.post.statuses__update(status=new_status)
        ids = weibo_api.get.statuses__user_timeline()
        print 'user_timeline: '
        print ids


def check():
    ups = UserProfile.objects.all()
    print len(ups)
    for up in ups:
        print 'profile_url:', up.kindle_profile_url
        if up.kindle_profile_url == '':
            print 'Not profile_url:', up.user.username
            continue
        (shared_urls, latest_shared) = check_profile_page(profile_url=up.kindle_profile_url)
        # user = User.objects.get(pk=up.user)
        # for i in range(len(shared_urls)):
        #     highlight = Highlight(user=user, url=shared_urls[i], \
        #             text=latest_shared[i].string)
        #     highlight.save()
        #     print highlight.text[:20]
        print 'Fetch %s new Highlights' % len(shared_urls)
        test_weibo_api(up)


def check_profile_page(profile_url='', timeout=20):
    profile_url = 'https://kindle.amazon.com/profile/%s' % profile_url
    page = urlopen(profile_url)
    if page.getcode() != 200:
        print "Error: %s" % page.getcode()
    soup = BS(page, from_encoding='utf8')

    def _get_shared_tags(tag):
        return tag.has_key('href') and tag['href'].startswith('/post/')

    shared_posts = soup.find_all(_get_shared_tags)
    new_posts = []
    new_urls = []
    for hl in shared_posts:
        hl_url = hl['href']
        if Highlight.objects.filter(url=hl_url).exists():
            break
        new_posts.append(hl)
        new_urls.append(hl_url)
    new_highlights = [share.find_next('div', {'class': 'sampleHighlight'}) \
            for share in new_posts]
    return (new_urls[::-1], new_highlights[::-1])
