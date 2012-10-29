from django.conf.urls.defaults import url, include, patterns
from django.contrib import admin
from django.views.generic.simple import direct_to_template

from haystack.views import SearchView  
from haystack.query import SearchQuerySet

sqs = SearchQuerySet().order_by('name')

from tastypie.api import Api
#from myapp.api import EntryResource, UserResource



v1_api = Api(api_name='v1')
#v1_api.register(UserResource())
#v1_api.register(EntryResource())



admin.autodiscover()


urlpatterns = patterns('',
                       url(r"^$", "games.views.homepage", name="home"),

                       (r'^favicon\.ico$', 'django.views.generic.simple.redirect_to', {'url': 'http://media.socceroutsider.com/images/favicon.ico'}),

                       (r'^about/$', direct_to_template, {'template': 'about.html'}),
                       (r'^api/$', direct_to_template, {'template': 'api.html'}),
                       #(r'^sources/$', direct_to_template, {'template': 'sources.html'}),

                       #(r'^blog/$', direct_to_template, {'template': 'blog.html'}),

                       url(r'search/', 
                           SearchView(load_all=False, searchqueryset=sqs),
                           name='haystack_search',  
                           ),
                       #include('haystack.urls')),



                       url(r'^awards/', include('awards.urls')),
                       url(r'^bios/', include('bios.urls')),
                       url(r'^c/', include('competitions.urls')),
                       url(r'^contact/', include('contact.urls')),
                       url(r'^dates/', include('dates.urls')),
                       url(r'^drafts/', include('drafts.urls')),
                       url(r'^games/', include('games.urls')),
                       url(r'^goals/', include('goals.urls')),
                       url(r'^graphs/', include('graphs.urls')),
                       url(r'^lineups/', include('lineups.urls')),
                       url(r'^money/', include('money.urls')),
                       url(r'^news/', include('news.urls')),
                       url(r'^positions/', include('positions.urls')),
                       url(r'^places/', include('places.urls')),
                       url(r'^sources/', include('sources.urls')),
                       url(r'^standings/', include('standings.urls')),
                       url(r'^stats/', include('stats.urls')),
                       url(r'^teams/', include('teams.urls')),
                       url(r'^tools/', include('tools.urls')),

                       # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
                       # to INSTALLED_APPS to enable admin documentation:
                           (r'^admin/doc/', include('django.contrib.admindocs.urls')),
                       # Uncomment the next line to enable the admin:
                               (r'^admin/', include(admin.site.urls)),
)
