# coding=utf8

from django.contrib import admin
from iread.accounts.models import UserProfile

class UserProfileAdmin(admin.ModelAdmin):
    search_fields = ['user', 'douban_id', 'weibo_id', 'email', 'kindle_profile_url']
    list_display = ['user', 'douban_id', 'weibo_id', 'email', \
            'kindle_profile_url', 'share_to_weibo', 'share_to_douban', \
            'weibo_tokens', 'douban_tokens']

admin.site.register(UserProfile, UserProfileAdmin)
