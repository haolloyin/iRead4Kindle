# coding=utf8

from django.contrib.auth.models import User
from django.db import models

class Highlight(models.Model):
    user = models.ForeignKey(User)
    url = models.CharField(max_length=128, blank=True, null=True)
    text = models.TextField(max_length=1024)
    remark = models.CharField(max_length=128, blank=True, null=True)
    book = models.CharField(max_length=128, blank=True, null=True)
    author = models.CharField(max_length=128, blank=True, null=True)
    added = models.DateTimeField(auto_now_add=True)

    is_shared_douban = models.BooleanField(default=False)
    is_shared_weibo = models.BooleanField(default=False)
    fetch_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-id', '-added']

    def __unicode__(self):
        return '%s: %s ...' % (self.user.username, self.text[:20])

    def author(self):
        return self.user.get_profile().get_kindle_name()

    def title(self):
        return self.text[:20]

    def get_url(self):
        return 'https://kindle.amazon.com%s' % self.url
