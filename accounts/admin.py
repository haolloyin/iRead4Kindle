# coding=utf8

from django.contrib import admin
from iRead4Kindle.accounts.models import UserProfile

class UserProfileAdmin(admin.ModelAdmin):
    search_fields = ['user', 'douban_id', 'weibo_id', 'email', 'kindle_profile_url']
    list_display = ['user', 'douban_id', 'weibo_id', 'kindle_profile_url', 'share_to_weibo', 'weibo_tokens', 'share_to_douban', 'douban_tokens', 'email']

admin.site.register(UserProfile, UserProfileAdmin)
