from django.conf.urls import url, include, patterns
#from django.conf.urls.defaults import url, include, patterns

from django.contrib import admin
from django.views.generic import RedirectView, TemplateView

#from haystack.views import SearchView  
#from haystack.query import SearchQuerySet

#sqs = SearchQuerySet().order_by('name')

admin.autodiscover()


urlpatterns = patterns('',
                       url(r"^$", "games.views.homepage", name="home"),
                       
                       #url(r'^sitemap\.xml$', 'django.contrib.sitemaps.views.sitemap', {'sitemaps': sitemaps}),

                       url(r'^favicon\.ico$', RedirectView.as_view(url='http://media.socceroutsider.com/images/favicon.ico'), name="favicon"),

                       url(r'^about/$', TemplateView.as_view(template_name='about/index.html'), name='about_index'),
                       url(r'^about/news/$', TemplateView.as_view(template_name='about/news.html'), name='about_news'),
                       url(r'^about/build/$', TemplateView.as_view(template_name='about/build.html'), name='about_build'),
                       
                       #(r'^api/$', TemplateView.as_view(template_name='api.html'), name='api'),
                       #(r'^sources/$', direct_to_template, {'template': 'sources.html'}),
                       #(r'^blog/$', direct_to_template, {'template': 'blog.html'}),

                       #url(r'search/', 
                       #    SearchView(load_all=False, searchqueryset=sqs),
                       #    name='haystack_search',  
                       #    ),
                       #include('haystack.urls')),

                       url(r"^calendar/$", "dates.views.calendar", name="calendar_index"),
                       url(r'^awards/', include('awards.urls')),
                       url(r'^bios/', include('bios.urls')),
                       url(r'^c/', include('competitions.urls')),
                       url(r'^contact/', include('contact.urls')),
                       url(r'^dates/', include('dates.urls')),
                       url(r'^drafts/', include('drafts.urls')),
                       url(r'^events/', include('events.urls')),
                       url(r'^games/', include('games.urls')),
                       url(r'^goals/', include('goals.urls')),
                       url(r'^graphs/', include('graphs.urls')),
                       #url(r'^images/', include('images.urls')),
                       url(r'^levels/', include('levels.urls')),
                       url(r'^lineups/', include('lineups.urls')),
                       url(r'^money/', include('money.urls')),
                       url(r'^news/', include('news.urls')),
                       url(r'^organizations/', include('organizations.urls')),
                       url(r'^positions/', include('positions.urls')),
                       url(r'^places/', include('places.urls')),
                       url(r'^sources/', include('sources.urls')),
                       url(r'^standings/', include('standings.urls')),
                       url(r'^stats/', include('stats.urls')),
                       url(r'^teams/', include('teams.urls')),
                       #url(r'^tools/', include('tools.urls')),
                       url(r'^videos/', include('videos.urls')),

                       # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
                       # to INSTALLED_APPS to enable admin documentation:
                           (r'^admin/doc/', include('django.contrib.admindocs.urls')),
                       # Uncomment the next line to enable the admin:
                               (r'^admin/', include(admin.site.urls)),
)
