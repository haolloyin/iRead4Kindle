
from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('iRead4Kindle.highlights.views',
    url(r'^$', 'index', name='highlights_index'),
    url(r'^detail/(?P<post_id>.*)/$', 'highlight_detail', name='highlight_detail'),

    url(r'^check/$', 'check_highlight_updates', name='check_highlight_updates'),
    url(r'^check_and_share/$', 'single_user_check_and_share', name='check_and_share'),

    url(r'^reader/(?P<username>.*)/start/(?P<start>.*)/end/(?P<end>.*)/$', 'highlights', name='highlights'),
)

