# coding=utf8

from urllib2 import urlopen
USE_BS4 = False
try:
    from bs4 import BeautifulSoup as BS
    USE_BS4 = True
except:
    # BeautifulSoup-3.2.1
    from iRead4Kindle.utils.BeautifulSoup import BeautifulSoup as BS

from django.contrib.auth.models import User, AnonymousUser
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext

from iRead4Kindle.accounts.models import UserProfile
from iRead4Kindle.accounts import utils as social_api
from iRead4Kindle.accounts.weibo import APIError as WeiboAPIError
from iRead4Kindle.highlights.models import Highlight
from iRead4Kindle.utils.decorators import admin_required

def index(request):
    if isinstance(request.user, AnonymousUser):
        messages.error(request, '当前您为匿名用户，没有 Kindle Highlights，请授权登录或注册后填写 Kindle Profile URL')
        return HttpResponseRedirect('/')

    highlights = Highlight.objects.filter(user=request.user)
    if not highlights:
        # return HttpResponseRedirect(reverse('highlights_index'))
        return HttpResponseRedirect(reverse('site_login'))
    kindle_name = request.user.get_profile().get_kindle_name()
    return render_to_response('highlights.html', \
            {'highlights': highlights, 'kindle_name': kindle_name}, \
            context_instance=RequestContext(request))


def highlight_detail(request, post_id):
    post_id = '/post/%s' % post_id
    hl = Highlight.objects.filter(url=post_id)
    if not hl:
        return HttpResponseRedirect(reverse('highlights_index'))
    kindle_name = request.user.get_profile().get_kindle_name()
    return render_to_response('highlights.html', \
            {'highlights': hl, 'kindle_name': kindle_name}, \
            context_instance=RequestContext(request))


def highlights(request, username, start, end):
    '''
    highlights/reader/2585443/start/3SIV34360UH0D/end/2PHTKF6EH81O3/
    '''
    up = UserProfile.objects.get(kindle_profile_url__contains=username)
    hls = Highlight.objects.filter(user=up.user)
    start_id = hls.get(url__contains=start).pk
    end_id = hls.get(url__contains=end).pk
    hls = hls.filter(pk__gte=start_id).filter(pk__lte=end_id)[::-1]
    if not hls or len(hls) == 0:
        return HttpResponseRedirect(reverse('highlights_index'))
    kindle_name = up.get_kindle_name()
    return render_to_response('highlights.html', \
            {'highlights': hls, 'kindle_name': kindle_name}, \
            context_instance=RequestContext(request))


def update_weibo(up=None, text=''):
    if up is None or text == '':
        return None
    try:
        weibo_api = social_api.get_weibo_api(up.weibo_id, \
                token_dict=up.get_weibo_tokens_dict())
        result = weibo_api.post.statuses__update(status=text)
        # get weibo mid for visiting the status update abobe
        mid = weibo_api.get.statuses__querymid(id=result['id'], type=1)
        status_url = 'http://weibo.com/%s/%s' % (result['user']['id'], mid['mid'])
        return status_url
    except WeiboAPIError, e:
        print e


def single_user_check_and_share(request):
    user = request.user
    up = user.get_profile()
    msg = ''
    if up.kindle_profile_url == '':
        msg = 'You have not provide Your Kindle Profile URL'
        messages.error(request, msg)
        return HttpResponseRedirect(reverse('accounts_profile'))

    # fetch new highlights
    hl_urls, new_hls = fetch_new_highlights(request, \
            profile_url=up.kindle_profile_url)

    if len(hl_urls) == 0 or len(new_hls) == 0:
        msg = 'You have no new Kindle highlights'
        messages.error(request, msg)
        return HttpResponseRedirect(reverse('accounts_profile'))

    # save new highlights
    user = User.objects.get(pk=up.user.id)
    url_len = len(hl_urls)
    for i in range(url_len):
        highlight = Highlight(user=user, url=hl_urls[i], \
                text=new_hls[i].text.strip())
        highlight.save()

    # share to weibo
    status_url = ''
    if up.has_weibo_oauth() and up.share_to_weibo:
        url = ''
        hl_text = new_hls[0].text.strip()
        hl_text = hl_text[:100]+'...' if len(hl_text) > 100 else hl_text
        if url_len > 1:
            reader = up.get_kindle_uid()
            start = hl_urls[0].split('/')[2]
            end = hl_urls[url_len-1].split('/')[2]
            url = 'http://%s/highlights/reader/%s/start/%s/end/%s/' % (request.META['HTTP_HOST'], reader, start, end)
        else:
            url = 'http://%s/highlights/detail%s' % (request.META['HTTP_HOST'], hl_urls[0].split('/')[2])

        weibo_text = u'『%s』%s #iRead4Kindle#' % (hl_text, url)
        status_url = update_weibo(up=up, text=weibo_text)

    status_url = '<a href="%s">%s</a>' % (status_url, status_url)
    msg = '%s highlights has ben saved/shared.\n%s' % (url_len, status_url)
    messages.success(request, msg)
    return HttpResponseRedirect(reverse('accounts_profile'))


@admin_required
def check_highlight_updates(request):
    ups = UserProfile.objects.all()
    for up in ups:
        if up.kindle_profile_url == '':
            continue

        hl_urls, new_hls = fetch_new_highlights(request, \
                profile_url=up.kindle_profile_url)
        if len(hl_urls) == 0 or len(new_hls) == 0:
            continue
        # save new highlights
        user = User.objects.get(pk=up.user.id)
        url_len = len(hl_urls)
        for i in range(url_len):
            highlight = Highlight(user=user, url=hl_urls[i], \
                    text=new_hls[i].text.strip())
            highlight.save()

        if up.has_weibo_oauth():
            hl_text = new_hls[0].text.strip()
            hl_text = hl_text[:100]+'...' if len(hl_text) > 100 else hl_text
            if url_len > 1:
                reader = up.get_kindle_uid()
                start = hl_urls[0].split('/')[2]
                end = hl_urls[url_len-1].split('/')[2]
                url = 'http://%s/highlights/reader/%s/start/%s/end/%s/' % (request.META['HTTP_HOST'], reader, start, end)
            else:
                url = 'http://%s/highlights/detail%s' % (request.META['HTTP_HOST'], hl_urls[0].split('/')[2])

            weibo_text = u'『%s』%s #iRead4Kindle#' % (hl_text, url)
            update_weibo(up=up, text=weibo_text)

        #TODO: share to douban

    msg = 'Highlights has ben saved & shared:'
    messages.success(request, msg)
    return HttpResponseRedirect(reverse('accounts_profile'))


def fetch_new_highlights(request, profile_url='', offset=0, new_urls=[], new_hls=[], timeout=20):
    assert new_urls != None
    assert new_hls != None

    p_url = 'https://kindle.amazon.com/profile/%s' % profile_url
    if offset != 0:
        p_url += '?offset=%s' % str(offset)

    page = urlopen(p_url)
    if page.getcode() != 200:
        messages.error(request, 'urlopen() error: %s' % page.getcode())
        return HttpResponseRedirect(reverse('accounts_profile'))

    if USE_BS4:
        soup = BS(page, from_encoding='utf8')
    else:
        soup = BS(page, fromEncoding='utf8')

    def _get_shared_tags(tag):
        return tag.has_key('href') and tag['href'].startswith('/post/')

    if USE_BS4:
        shared_posts = soup.find_all(_get_shared_tags)
    else:
        shared_posts = soup.findAll(_get_shared_tags)

    if len(shared_posts) < 1:
        #assert False
        return (new_urls[::-1], new_hls[::-1])

    posts = []
    urls = []
    no_fetched = len(shared_posts)
    for hl in shared_posts:
        hl_url = hl['href']
        if Highlight.objects.filter(url=hl_url).exists():
            no_fetched -= 1
            continue
        posts.append(hl)
        urls.append(hl_url)
    if USE_BS4:
        new_hls.extend([share.find_next('div', {'class': 'sampleHighlight'}) \
                for share in posts])
    else:
        new_hls.extend([share.findNext('div', {'class': 'sampleHighlight'}) \
                for share in posts])
    new_urls.extend(urls)

    # fetch more new highlights if no_fetched > 2 on one page
    if no_fetched > 2:
        offset += len(shared_posts)
        fetch_new_highlights(request, profile_url=profile_url, offset=offset, \
                new_urls=new_urls, new_hls=new_hls)

    return (new_urls[::-1], new_hls[::-1])

