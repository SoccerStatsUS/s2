from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('competitions.views', 
                       url(r'^$',
                           'competition_index',
                           name='competition_index'),


                       url(r'^s/names/$',
                           'season_names',
                           name='season_names'),


                       url(r'^s/(?P<season_slug>[a-z0-9-]+)/$',
                           'season_list',
                           name='season_list'),


                       url(r'^level/(?P<level_slug>[a-z0-9-]+)/$',
                           'level_detail',
                           name='level_detail'),


                       url(r'^r/$',
                           'random_competition_detail',
                           name='random_competition_detail'),

                       url(r'^(?P<competition_slug>[a-z0-9-]+)/$',
                           'competition_detail',
                           name='competition_detail'),


                       url(r'^(?P<competition_slug>[a-z0-9-]+)/stats/$',
                           'competition_stats',
                           name='competition_stats'),

                       url(r'^(?P<competition_slug>[a-z0-9-]+)/attendance/$',
                           'competition_attendance',
                           name='competition_attendance'),


                       url(r'^(?P<competition_slug>[a-z0-9-]+)/games/$',
                           'competition_games',
                           name='competition_games'),




                       url(r'^(?P<competition_slug>[a-z0-9-]+)/(?P<season_slug>[a-z0-9-]+)/$',
                           'season_detail',
                           name='season_detail'),

                       url(r'^(?P<competition_slug>[a-z0-9-]+)/(?P<season_slug>[a-z0-9-]+)/stats/$',
                           'season_stats',
                           name='season_stats'),

                       url(r'^(?P<competition_slug>[a-z0-9-]+)/(?P<season_slug>[a-z0-9-]+)/games/$',
                           'season_games',
                           name='season_games'),

                       url(r'^(?P<competition_slug>[a-z0-9-]+)/(?P<season_slug>[a-z0-9-]+)/goals/$',
                           'season_goals',
                           name='season_goals'),

                       url(r'^(?P<competition_slug>[a-z0-9-]+)/(?P<season_slug>[a-z0-9-]+)/attendance/$',
                           'season_attendance',
                           name='season_attendance'),


                       url(r'^(?P<competition_slug>[a-z0-9-]+)/(?P<season_slug>[a-z0-9-]+)/salaries/$',
                           'season_salaries',
                           name='season_salaries'),



                       url(r'^(?P<competition_slug>[a-z0-9-]+)/(?P<season_slug>[a-z0-9-]+)/graphs/$',
                           'season_graphs',
                           name='season_graphs'),


                       )
