# coding=utf8


import time

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save


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

    weibo_tokens = models.CharField(default='', max_length=100, null=True, blank=True)
    douban_tokens = models.CharField(default='', max_length=100, null=True, blank=True)

    def email(self):
        return self.user.email

    def weibo_access_tokens(self):
        if self.weibo_tokens != '':
            tokens = self.weibo_tokens.split('_')
            return {'access_token': tokens[0], 'expires_in': float(tokens[1])}
        return None

    def douban_access_tokens(self):
        if self.douban_tokens != '':
            tokens = self.douban_tokens.split('_')
            return {'access_token': tokens[0], 'token_secret': tokens[1]}
        return None

    def is_weibo_expires(self):
        return not self.weibo_tokens or \
                time.time() > self.weibo_access_token()['expires_in']

    def share_2_weibo(self):
        pass

def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

post_save.connect(create_user_profile, sender=User)
