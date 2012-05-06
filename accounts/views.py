# coding=utf8

from cgi import parse_qs

from iRead4Kindle.accounts import pydouban, weibo
from iRead4Kindle.accounts.utils import create_or_update_user, get_user_from_uuid
from iRead4Kindle.accounts.models import UUID, UserProfile

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import AnonymousUser, User
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.urlresolvers import reverse


def profile(request):
    if request.method == 'POST':
        user = request.user
        profile = user.get_profile()

        profile_url = request.POST['kindle_frofile_url'][34:].split('/')
        if len(profile_url) == 2:
            first_name = profile_url[0]
            last_name = profile_url[1]
            if (first_name and user.first_name != first_name) \
                    or (last_name and user.last_name != last_name):
                messages.success(request, 'Kindle profile 更新成功')
                user.first_name = first_name
                user.last_name = last_name
                user.save()
                profile.kindle_profile_url = user.first_name + '/' + \
                        user.last_name
        share_to_weibo = request.POST.get('share_to_weibo', None)
        share_to_douban = request.POST.get('share_to_douban', None)
        profile.share_to_weibo = (share_to_weibo is not None)
        profile.share_to_douban = (share_to_douban is not None)
        m = '%s 自动发布 %s'
        if profile.share_to_weibo:
            msg = m % ('设置', '微博')
        else:
            msg = m % ('取消', '微博')
        messages.success(request, msg)
        if profile.share_to_douban:
            msg = m % ('设置', '豆瓣广播')
        else:
            msg = m % ('取消', '豆瓣广播')
        messages.success(request,msg)
        profile.save()
        return HttpResponseRedirect(reverse('accounts_profile'))
    else:
        user = request.user
        profile = user.get_profile()
        profile_url = ''
        if profile.kindle_profile_url != '':
            profile_url = 'https://kindle.amazon/profile/%s' % \
                    profile.kindle_profile_url
        info = {'kindle_profile_url': profile_url,
                'has_weibo_oauth': True if profile.weibo_access_tokens() else False,
                'share_to_weibo': profile.share_to_weibo,
                'has_douban_oauth': True if profile.douban_access_tokens() else False,
                'share_to_douban': profile.share_to_douban,
                }
        return render_to_response('profile.html', \
                info, context_instance=RequestContext(request))


def site_login(request):
    if not isinstance(request.user, AnonymousUser):
        return HttpResponseRedirect('/')

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        if username.split('@')[0] and \
                (username.endswith('@kindle.com') or \
                username.endswith('@free.kindle.com')):
            prefix = username.split('@')[0]
            result = User.objects.filter(email__startswith=prefix + '@',
                    email__endswith='kindle.com')
            if result and len(result) == 1:
                username = result[0].username
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            next_url = request.session.get('next_url', '')
            if next_url:
                del request.session['next_url']
            return HttpResponseRedirect(next_url or '/')
        else:
            messages.error(request,
                    'Invalid username or password, please try again.')
            return HttpResponseRedirect(reverse('site_login'))
    else:
        next_url = request.GET.get('next', '')
        if next_url:
            request.session['next_url'] = next_url
    return render_to_response('login.html', \
                context_instance=RequestContext(request))


def site_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('site_login'))


def login_with_weibo(request):
    client = weibo.APIClient(app_key=settings.WEIBO_API_KEY, \
            app_secret=settings.WEIBO_SECRET)
    callback_url = 'http://%s%s' % \
            (request.META['HTTP_HOST'], reverse('weibo_callback'))
    url = client.get_authorize_url(redirect_uri=callback_url)
    return HttpResponseRedirect(url)


def weibo_callback(request):
    client = weibo.APIClient(app_key=settings.WEIBO_API_KEY, \
            app_secret=settings.WEIBO_SECRET)
    callback_url = 'http://%s%s' % \
            (request.META['HTTP_HOST'], reverse('weibo_callback'))
    code = request.GET['code']
    token = client.request_access_token(code, redirect_uri=callback_url)
    '''
{'access_token': u'2.00Xe32uB0Sx3lC02e7ed88cbf31NcE', 'expires_in': 1336270249, 'remind_in': u'86399', 'uid': u'1748699617'}
    '''    
    client.set_access_token(token.access_token, token.expires_in)
    request.session['weibo_access_token'] = token.access_token
    request.session['weibo_user_id'] = token.uid

    # Create a new Weibo user if not exist
    weibo_id = request.session['weibo_user_id']
    user = create_or_update_user(weibo_id, 'weibo', \
            first_name=token.access_token, last_name=str(token.expires_in))
    user = authenticate(username='weibo_'+weibo_id, password='default')
    assert user is not None
    if user is not None:
        login(request, user)

    # Make sure to save the access_tokens
    # profile = UserProfile.objects.get(user=user.pk)
    profile = user.get_profile()
    weibo_tokens = token.access_token + '_' + str(token.expires_in)
    profile.weibo_access_tokens = weibo_tokens
    profile.weibo_user_id = token.uid
    profile.save()

    assert profile.weibo_access_tokens != '' and profile.weibo_user_id != ''
    next_url = request.session.get('next_url', '')
    if not next_url:
        next_url = reverse('accounts_profile')
    return HttpResponseRedirect(next_url)


def login_with_douban(request):
    auth = pydouban.Auth(key=settings.DOUBAN_API_KEY,
            secret=settings.DOUBAN_SECRET)
    callback_url = 'http://%s%s' % \
            (request.META['HTTP_HOST'], reverse('douban_callback'))
    dic = auth.login(callback=callback_url)
    key, secret = dic['oauth_token'], dic['oauth_token_secret']
    request.session['douban_request_secret'] = secret
    return HttpResponseRedirect(dic['url'])


def douban_callback(request):
    request_key = request.GET.get('oauth_token')
    request_secret = request.session.get('douban_request_secret')
    auth = pydouban.Auth(key=settings.DOUBAN_API_KEY,
            secret=settings.DOUBAN_SECRET)

    access_tokens = auth.get_acs_token(request_key, request_secret)
    tokens = parse_qs(access_tokens)
    '''
    {'douban_user_id': ['45742059'], 'oauth_token': ['bbef8848bf48657033ce98da3dd93050'], 'oauth_token_secret': ['b2302cccf9a9ef79']}
    '''
    request.session['douban_token'] = tokens['oauth_token'][0]
    request.session['douban_token_secret'] = tokens['oauth_token_secret'][0]
    request.session['douban_user_id'] = tokens['douban_user_id'][0]
    
    # Create a new Douban user if not exist
    douban_id = request.session['douban_user_id']
    user = create_or_update_user(douban_id, 'douban', \
            first_name=tokens['oauth_token'][0], \
            last_name=tokens['oauth_token_secret'][0])
    user = authenticate(username='douban_'+douban_id, password='default')
    assert user is not None
    if user is not None:
        login(request, user)

    # Make sure to save the access_tokens
    # profile = UserProfile.objects.get(user=user.pk)
    profile = user.get_profile()
    douban_tokens = request.session['douban_token'] + '_' + \
            request.session['douban_token_secret']
    profile.douban_access_tokens = douban_tokens
    profile.douban_id = 'douban_' + request.session['douban_user_id']
    profile.save()

    if 'douban_request_secret' in request.session:
        del request.session['douban_request_secret']
    next_url = request.session.get('next_url', '')
    if not next_url:
        next_url = reverse('accounts_profile')
    return HttpResponseRedirect(next_url)


def get_douban_api(request):
    if 'douban_oauth_token' not in request.session or \
            'douban_oauth_token_secret' not in request.session:
        return None
    api = pydouban.Api()
    token = request.session['douban_oauth_token']
    token_secret = request.session['douban_oauth_token_secret']
    api.set_oauth(key=settings.DOUBAN_API_KEY,
            secret=settings.DOUBAN_SECRET,
            acs_token=token,
            acs_token_secret=token_secret)
    return api


def signup(request):
    pass


def password_reset(request):
    url = reverse('site_login')

    uuid_string = request.GET.get('uuid')
    if uuid_string:
        if not get_user_from_uuid(uuid_string):
            return HttpResponse('Invalid URL')
        return render_to_response('accounts/password_reset.html',
                {'uuid': uuid_string, },
                context_instance=RequestContext(request))

    uuid_string = request.POST.get('uuid')
    if uuid_string:
        user = get_user_from_uuid(uuid_string)
        if not user:
            return HttpResponse('Invalid URL')

        url = reverse('accounts_password_reset') + '?uuid=' + uuid_string
        new_password = request.POST.get('password')
        new_password2 = request.POST.get('password2')
        if not new_password:
            messages.error(request, 'Password cannot be blank.')
            return HttpResponseRedirect(url)
        elif new_password != new_password2:
            messages.error(request, 'The password typed do not match, please try again.')
            return HttpResponseRedirect(url)
        else:
            user.set_password(new_password)
            user.save()
            UUID.objects.get(uuid=uuid_string).delete()
            messages.success(request, 'The password has been reset successfullly.')
            url = reverse('site_login')
            return HttpResponseRedirect(url)

    ## Branch else: Send reset URL to user's Kindle
    if request.method == "POST":
        email = request.POST.get('email')
        if not email or (not email.endswith('@kindle.com') and \
                         not email.endswith('@free.kindle.com')):
            messages.error(request, "Email address required.")
            return HttpResponseRedirect(url)
        elif not User.objects.filter(email__startswith=email.split("@")[0] + '@'):
            messages.error(request, "No user with this E-mail Address.")
            return HttpResponseRedirect(url)

        prefix = email.split('@')[0]
        result = User.objects.filter(email__startswith=prefix + '@',
            email__endswith='kindle.com')
        if result and len(result) == 1:
            user = result[0]
            uuid_string = str(uuid.uuid4())
            UUID.objects.create(user=user, uuid=uuid_string)
            reset_url = "http://kindle.io" + reverse("accounts_password_reset") + \
                        "?uuid=" + uuid_string
            text = "Hello,\n\nPlease click the following URL to reset your password. " \
                   "The URL will be invalid in 24 hours." \
                   "\n\n%s\n\nKindle.io" % reset_url
            # f = generate_file(text)
            # if not settings.DEBUG:
            #     send_files_to([f], [email])
            #     os.remove(f)
            messages.success(request,
                             "Password Reset URL has been sent to your Kindle."
                             " Please check it in a few minutes.")
    return HttpResponseRedirect(url)
