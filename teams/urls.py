from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('teams.views', 

                       url(r'^$',
                           'team_index',
                           name='team_index'),

                       url(r'^bad/?$',
                           'bad_teams',
                           name='bad_teams'),


                       url(r'^seasons/?$',
                           'seasons_dashboard',
                           name='seasons_dashboard'),


                       url(r'^(?P<team_slug>[a-z0-9-]+)/(?P<year>\d+)',
                           'team_year_detail',
                           name='team_year_detail'),

                       url(r'^(?P<team_slug>[a-z0-9-]+)',
                           'team_detail',
                           name='team_detail'),

                       url(r'^ajax$',
                           'teams_ajax',
                           name='teams_ajax'),



)
