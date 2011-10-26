from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('s2.teams.views', 

                       url(r'^$',
                           'team_index',
                           name='team_index'),

                       url(r'^seasons/$',
                           'seasons_dashboard',
                           name='seasons_dashboard'),


                       url(r'^(?P<team_slug>[a-z0-9-]+)/(?P<season_slug>[a-z0-9-]+)',
                           'team_season_detail',
                           name='team_season_detail'),

                       url(r'^(?P<team_slug>[a-z0-9-]+)',
                           'team_detail',
                           name='team_detail'),


)
