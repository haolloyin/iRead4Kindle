# coding=utf8


import time

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save


DOUBAN_LOGIN_FLAG = "loged_with_douban"
WEIBO_LOGIN_FLAG = "loged_with_weibo"

class UUID(models.Model):
    user = models.ForeignKey(User)
    uuid = models.CharField(max_length=40)
    added = models.DateTimeField(auto_now_add=True)


class UserProfile(models.Model):
    user = models.OneToOneField(User)

    douban_id = models.CharField(max_length=20, null=True, blank=True)
    weibo_id = models.CharField(max_length=40, null=True, blank=True)
    kindle_profile_url = models.CharField(default='', max_length=40, null=True, blank=True)

    share_to_weibo = models.BooleanField(default=False, help_text='发送微博')
    share_to_douban = models.BooleanField(default=False, help_text='发送豆瓣广播')

    weibo_tokens = models.CharField(default=None, max_length=100, null=True, blank=True)
    douban_tokens = models.CharField(default=None, max_length=100, null=True, blank=True)

    def email(self):
        return self.user.email

    def get_weibo_tokens_dict(self):
        if self.weibo_tokens is None or self.weibo_tokens == '':
            return None
        tokens = self.weibo_tokens.split('@')
        return {'access_token': tokens[0], 'expires_in': float(tokens[1])}

    def get_douban_tokens_dict(self):
        if self.douban_tokens is None or self.douban_tokens == '':
            return None
        tokens = self.douban_tokens.split('@')
        return {'access_token': tokens[0], 'token_secret': tokens[1]}

    def has_weibo_oauth(self):
        return (True if self.get_weibo_tokens_dict() else False)

    def has_douban_oauth(self):
        return (True if self.get_douban_tokens_dict() else False)

    def is_weibo_expires(self):
        return not self.weibo_tokens or \
                time.time() > float(self.weibo_access_token()['expires_in'])

    def get_kindle_name(self):
        if self.kindle_profile_url != '':
            return self.kindle_profile_url.split('/')[0]

def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

post_save.connect(create_user_profile, sender=User)
