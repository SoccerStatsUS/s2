from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('soccer.teams.views', 
                       url(r'^$', 'index', name='teams_index'),
                       url(r'^defunct/$', 'defunct', name='defunct_index'),

                       url(r'^(?P<slug>[a-zA-Z0-9_.-]+)/$',
                           'team_detail',
                           name='team_detail'),

)
