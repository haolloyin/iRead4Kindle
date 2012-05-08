# coding=utf8

from urllib2 import urlopen
from bs4 import BeautifulSoup as BS

from django.contrib.auth.models import User
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext

from iRead4Kindle.accounts.models import UserProfile
from iRead4Kindle.accounts import utils as social_api
from iRead4Kindle.highlights.models import Highlight

def index(request):
    highlights = Highlight.objects.filter(user=request.user)
    if not highlights:
        return HttpResponseRedirect(reverse('highlights_index'))
    kindle_name = request.user.get_profile().get_kindle_name()
    return render_to_response('highlights.html', \
            {'highlights': highlights, 'kindle_name': kindle_name}, \
            context_instance=RequestContext(request))


def check_highlight_updates(request):
    ups = UserProfile.objects.all()
    for up in ups:
        if up.kindle_profile_url == '':
            continue

        hl_urls, new_hls = fetch_new_highlights(request, \
                profile_url=up.kindle_profile_url)
        # save new highlights
        user = User.objects.get(pk=up.user.id)
        for i in range(len(hl_urls)):
            highlight = Highlight(user=user, url=hl_urls[i], \
                    text=new_hls[i].text)
            highlight.save()

        #TODO share to weibo and douban
        if up.has_weibo_oauth():
            weibo_tokens = up.get_weibo_tokens_dict()
            weibo_api = social_api._get_weibo_api(up.weibo_id, \
                    weibo_tokens['access_token'], weibo_tokens['expires_in'])
            weibo_api
    messages.success(request, 'Highlights has ben saved')
    return HttpResponseRedirect(reverse('accounts_profile'))


    # for up in ups:
    #     if (not up.has_weibo_oauth()) or (not up.share_to_weibo) or \
    #             up.kindle_profile_url == '':
    #         continue
    #     weibo_tokens = up.get_weibo_tokens_dict()
    #     weibo_api = social_api._get_weibo_api(up.weibo_id, \
    #             weibo_tokens['access_token'], weibo_tokens['expires_in'])
        


def fetch_new_highlights(request, profile_url='', timeout=20):
    profile_url = 'https://kindle.amazon.com/profile/%s' % profile_url
    page = urlopen(profile_url)
    if page.getcode() != 200:
        messages.error(request, 'profile page fetch error: %s' % page.getcode())
        return HttpResponseRedirect(reverse('accounts_profile'))
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
