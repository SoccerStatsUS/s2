from django.conf.urls.defaults import url, include, patterns
from django.contrib import admin
from django.views.generic.simple import direct_to_template

from tastypie.api import Api
#from myapp.api import EntryResource, UserResource

v1_api = Api(api_name='v1')
#v1_api.register(UserResource())
#v1_api.register(EntryResource())



admin.autodiscover()


urlpatterns = patterns('',
                       url(r"^$", "s2.games.views.homepage", name="home"),

                       (r'^favicon\.ico$', 'django.views.generic.simple.redirect_to', {'url': 'http://media.socceroutsider.com/images/favicon.ico'}),

                       (r'^about/$', direct_to_template, {'template': 'about.html'}),
                       (r'^api/$', direct_to_template, {'template': 'api.html'}),
                       (r'^sources/$', direct_to_template, {'template': 'sources.html'}),

                       url(r'search/', include('haystack.urls')),

                       url(r'^awards/', include('s2.awards.urls')),
                       url(r'^bios/', include('s2.bios.urls')),
                       url(r'^c/', include('s2.competitions.urls')),
                       url(r'^contact/', include('s2.contact.urls')),
                       url(r'^dates/', include('s2.dates.urls')),
                       url(r'^drafts/', include('s2.drafts.urls')),
                       url(r'^games/', include('s2.games.urls')),
                       url(r'^goals/', include('s2.goals.urls')),
                       url(r'^lineups/', include('s2.lineups.urls')),
                       url(r'^managers/', include('s2.positions.urls')),
                       
                       url(r'^places/', include('s2.places.urls')),
                       url(r'^teams/', include('s2.teams.urls')),
                       url(r'^standings/', include('s2.standings.urls')),
                       url(r'^stats/', include('s2.stats.urls')),

                       # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
                       # to INSTALLED_APPS to enable admin documentation:
                           (r'^admin/doc/', include('django.contrib.admindocs.urls')),
                       # Uncomment the next line to enable the admin:
                               (r'^admin/', include(admin.site.urls)),
)
