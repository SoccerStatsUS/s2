from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('teams.views', 

                       url(r'^$',
                           'team_index',
                           name='team_index'),

                       url(r'^az/(?P<fragment>.+)/$',
                           'team_name_fragment',
                           name='team_name_fragment'),
                       
                       url(r'^bad/$',
                           'bad_teams',
                           name='bad_teams'),


                       url(r'^seasons/$',
                           'seasons_dashboard',
                           name='seasons_dashboard'),

                       url(r'^standings/$',
                           'team_standings',
                           name='team_standings'),

                       url(r'^(?P<team_slug>[a-z0-9-]+)/(?P<year>\d+)/$',
                           'team_year_detail',
                           name='team_year_detail'),

                       url(r'^r/$',
                           'random_team_detail',
                           name='random_team_detail'),


                       url(r'^(?P<team_slug>[a-z0-9-]+)/$',
                           'team_detail',
                           name='team_detail'),


                       url(r'^(?P<team_slug>[a-z0-9-]+)/stats/$',
                           'team_stats',
                           name='team_stats'),

                       url(r'^(?P<team_slug>[a-z0-9-]+)/picks/$',
                           'team_picks',
                           name='team_picks'),


                       url(r'^(?P<team_slug>[a-z0-9-]+)/draftees/$',
                           'team_draftees',
                           name='team_draftees'),

                       url(r'^(?P<team_slug>[a-z0-9-]+)/games/$',
                           'team_games',
                           name='team_games'),

                       url(r'^(?P<team_slug>[a-z0-9-]+)/graphs/$',
                           'team_graphs',
                           name='team_graphs'),


                       url(r'^(?P<team_slug>[a-z0-9-]+)/calendar/$',
                           'team_calendar',
                           name='team_calendar'),



                       url(r'^(?P<team1_slug>[a-z0-9-]+)/v/(?P<team2_slug>[a-z0-9-]+)$',
                           'team_versus',
                           name='team_versus'),

                       url(r'^(?P<team_slug>[a-z0-9-]+)/c/(?P<competition_slug>[a-z0-9-]+)$',
                           'team_competition_detail',
                           name='team_competition_detail'),


                       url(r'^ajax$',
                           'teams_ajax',
                           name='teams_ajax'),



)
