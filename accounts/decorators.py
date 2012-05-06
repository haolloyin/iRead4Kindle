from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import user_passes_test
from iRead4Kindle.accounts.models import UserProfile, DOUBAN_LOGIN_FLAG, WEIBO_LOGIN_FLAG


def is_authenticated(user):
    return user.is_authenticated() or \
        hasattr(user, DOUBAN_LOGIN_FLAG) or \
        hasattr(user, WEIBO_LOGIN_FLAG)


def login_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url=None):
    """
    Decorator for views that checks that the user is logged in, redirecting
    to the log-in page if necessary.
    """
    actual_decorator = user_passes_test(
        is_authenticated,
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator

