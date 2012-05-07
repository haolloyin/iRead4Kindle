
from datetime import timedelta

from django.contrib import auth
from django.contrib.auth.models import User
from django.conf import settings

from iRead4Kindle.accounts.models import UserProfile, UUID


def get_user_from_uuid(uuid):
    date_limit = now() - timedelta(days=1)
    uuids = UUID.objects.filter(uuid=uuid, added__gte=date_limit)
    if not uuids or len(uuids) != 1:
        return None
    return uuids[0].user


def create_or_update_user(user_id, user_type, first_name='', last_name=''):
    '''
    user_type must be either 'douban' or 'weibo'
    '''
    if not user_id or not user_type:
        return

    if user_type not in ('douban', 'weibo'):
        return

    username = user_type + '_' + user_id
    if User.objects.filter(username=username).exists():
        user = User.objects.get(username=username)
    else:
        user = User.objects.create_user(username=username,
                email='invalid@kindle.com', password='default')
    user.first_name = first_name
    user.last_name = last_name
    user.save()

    try:
        profile = user.get_profile()
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=user)

    user_type_name = user_type + '_id'
    if getattr(profile, user_type_name) != user_id:
        setattr(profile, user_type_name, user_id)
        tokens = first_name + '@' + last_name
        setattr(profile, user_type + '_tokens', tokens)
        profile.save()
    # user_logged_in.send(sender=user.__class__, user=user)
    #auth.login(request, user)
    return user


def _get_weibo_api(weibo_id='', access_token=None, expires_in=None):
    from weibo import APIClient
    if weibo_id != '' and access_token:
        api = APIClient(app_key=settings.WEIBO_API_KEY, \
                app_secret=settings.WEIBO_SECRET)
        api.set_access_token(access_token, expires_in=expires_in)
        return api
    return None



def _get_douban_api(douban_id='', access_token=None, token_secret=None):
    from pydouban import Api
    if douban_id != '' and access_token and token_secret:
        api = Api()
        api.set_oauth(key=settings.DOUBAN_API_KEY, \
                    secret=settings.DOUBAN_SECRET, \
                    acs_token=access_token, \
                    acs_token_secret=token_secret)
        return api
    return None
