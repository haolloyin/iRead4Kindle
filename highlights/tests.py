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
'''
from iRead4Kindle.highlights import tests
tests.check()
'''


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
        ids = weibo_api.get.statuses__user_timeline__ids()
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
