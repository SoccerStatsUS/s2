from django.conf.urls.defaults import url, include, patterns
from django.contrib import admin
from django.views.generic.simple import direct_to_template


admin.autodiscover()

urlpatterns = patterns('',
                       url(r'^$', direct_to_template, {'template': 'index.html'}),
                       url(r'^bios/', include('s2.bios.urls')),
                       url(r'^games/', include('s2.games.urls')),
                       url(r'^goals/', include('s2.goals.urls')),

                       # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
                       # to INSTALLED_APPS to enable admin documentation:
                           (r'^admin/doc/', include('django.contrib.admindocs.urls')),
                       # Uncomment the next line to enable the admin:
                           (r'^admin/', include(admin.site.urls)),
)
