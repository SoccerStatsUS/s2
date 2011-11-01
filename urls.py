from django.conf.urls.defaults import url, include, patterns
from django.contrib import admin
from django.views.generic.simple import direct_to_template


admin.autodiscover()


urlpatterns = patterns('',
                       #url(r'^$', direct_to_template, {'template': 'index.html'}),
                       url(r"^$", "s2.games.views.homepage", name="home"),
                       url(r'^bios/', include('s2.bios.urls')),
                       url(r'^c/', include('s2.competitions.urls')),
                       url(r'^dates/', include('s2.dates.urls')),
                       url(r'^drafts/', include('s2.drafts.urls')),
                       url(r'^games/', include('s2.games.urls')),
                       url(r'^goals/', include('s2.goals.urls')),
                       url(r'^teams/', include('s2.teams.urls')),

                       url(r'^stats/', include('s2.stats.urls')),

                       # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
                       # to INSTALLED_APPS to enable admin documentation:
                           (r'^admin/doc/', include('django.contrib.admindocs.urls')),
                       # Uncomment the next line to enable the admin:
                           (r'^admin/', include(admin.site.urls)),
)
