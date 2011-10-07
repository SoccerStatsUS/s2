from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('s2.teams.views', 

                       url(r'^(?P<team_id>\d+)/$',
                           'team_detail',
                           name='team_detail'),

)
