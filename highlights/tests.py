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

'''
from iRead4Kindle.highlights import tests
tests.check()
'''

def check():
    ups = UserProfile.objects.all()
    print len(ups)
    for up in ups:
        print 'profile_url:', up.kindle_profile_url
        if up.kindle_profile_url == '':
            print 'Not profile_url:', up.user.username
            continue
        (shared_urls, latest_shared) = check_profile_page(profile_url=up.kindle_profile_url)
        user = User.objects.get(pk=up.user)
        for i in range(len(shared_urls)):
            highlight = Highlight(user=user, url=shared_urls[i], \
                    text=latest_shared[i].string)
            highlight.save()
            print highlight.text[:20]


def check_profile_page(profile_url='', timeout=20):
    profile_url = 'https://kindle.amazon.com/profile/%s' % profile_url
    print 'fetching:', profile_url
    page = urlopen(profile_url, timeout=timeout)
    if page.getcode() != 200:
        print 'Error: %s' % page.getcode()
    soup = BS(page, from_encoding='utf8')

    def _get_shared_tags(tag):
        return tag.has_key('href') and tag['href'].startswith('/post/')

    shared = soup.find_all(_get_shared_tags)
    print 'Shared:', len(shared)
    unsaved = []
    unsaved_urls = []
    for hl in shared:
        hl_url = hl['href']
        if Highlight.objects.filter(url=hl_url).exists():
            break
        unsaved.append(hl)
        unsaved_urls.append(hl_url)
    latest_shared = [share.find_next('span', {'class': 'sampleCloseQuote'}) \
            for share in unsaved]
    return (unsaved_urls, latest_shared)
