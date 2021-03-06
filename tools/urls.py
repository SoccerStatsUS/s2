from django.conf.urls import patterns, url

urlpatterns = patterns('tools.views', 

                       url(r'^$',
                           'tool_index',
                           name='tool_index'),


                       url(r'^games/$',
                           'game_search',
                           name='game_search'),

                       url(r'^stats/$',
                           'stat_search',
                           name='stat_search'),


                       url(r'^goals/$',
                           'goal_search',
                           name='goal_search'),


                       url(r'^lineups/$',
                           'lineup_search',
                           name='lineup_search'),


                       url(r'^ajax/games/$',
                           'games_ajax',
                           name='games_ajax'),

                       url(r'^ajax/gamesid/$',
                           'games_ajax_by_id',
                           name='games_ajax_by_id'),

                       url(r'^ajax/statsid/$',
                           'stats_ajax_by_id',
                           name='stats_ajax_by_id'),


                       url(r'^ajax/stats/$',
                           'stats_ajax',
                           name='stats_ajax'),


                       url(r'^ajax/goals/$',
                           'goals_ajax',
                           name='goals_ajax'),


                       url(r'^ajax/lineups/$',
                           'lineups_ajax',
                           name='lineups_ajax'),




)
