
from django.contrib import admin

from iRead4Kindle.highlights.models import Highlight

class HighlightAdmin(admin.ModelAdmin):
    search_fields = ['author', 'user', 'title', 'text']
    list_display = ('user', 'author', 'url', 'title', 'added', 'is_shared_weibo', \
            'is_shared_douban', 'fetch_time')
    list_filter = ('added', )

admin.site.register(Highlight, HighlightAdmin)
