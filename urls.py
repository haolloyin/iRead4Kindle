
from django.conf import settings
from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^iRead4Kindle/', include('iRead4Kindle.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),

    url(r'^$', 'iRead4Kindle.views.home', name='home'),
    url(r'^accounts/', include('iRead4Kindle.accounts.urls')),

    url(r'^login/$', 'iRead4Kindle.accounts.views.site_login', name='site_login'),
    url(r'^logout/$', 'iRead4Kindle.accounts.views.site_logout', name='site_logout'),
    
    url(r'highlights/', include('iRead4Kindle.highlights.urls')),


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
