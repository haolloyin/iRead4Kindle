
from django.conf import settings
from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^iread/', include('iread.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),

    url(r'^$', 'iread.views.home', name='home'),
    url(r'^accounts/', include('iread.accounts.urls')),

    url(r'^login/$', 'iread.accounts.views.site_login', name='site_login'),
    url(r'^logout/$', 'iread.accounts.views.site_logout', name='site_logout'),


)

if settings.DEBUG:
    # urlpatterns += patterns('',
    #     (r'^media/(?P<path>.*)$', 'django.views.static.serve', 
    #         {'document_root': settings.MEDIA_ROOT}),
    # )

    urlpatterns += patterns('',
        (r'^static/(?P<path>.*)$', 'django.views.static.serve', 
            {'document_root': settings.MEDIA_ROOT}),
    )
