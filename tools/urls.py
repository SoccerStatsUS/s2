from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('graphs.views', 

                       url(r'^$',
                           'tool_index',
                           name='tool_index'),


                       url(r'^games/$',
                           'game_search',
                           name='game_search'),


                       url(r'^goals/$',
                           'goal_search',
                           name='goal_search'),


                       url(r'^lineups/$',
                           'lineup_search',
                           name='lineup_search'),


)
