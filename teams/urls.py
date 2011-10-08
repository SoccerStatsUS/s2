from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('s2.teams.views', 

                       url(r'^$',
                           'team_index',
                           name='team_index'),


                       url(r'^(?P<team_slug>[a-z0-9-]+)',
                           'team_detail',
                           name='team_detail'),

)
