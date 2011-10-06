from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('soccer.teams.views', 

                       url(r'^(?P<slug>[a-zA-Z0-9_.-]+)/$',
                           'team_detail',
                           name='team_detail'),

)
