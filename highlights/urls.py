
from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('iRead4Kindle.highlights.views',
    url(r'^$', 'index', name='highlights_index'),
    url(r'^check/$', 'check_highlight_updates', name='check_highlight_updates'),
    #url(r'^config/$', 'config', name='notes_config'),
)

