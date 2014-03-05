from django.conf.urls import patterns, url

urlpatterns = patterns('games.views', 
                       url(r'^$',
                           'games_index',
                           name='games_index'),

                       url(r'^bad/$',
                           'bad_games',
                           name='bad_games'),


                       url(r'^r/$',
                           'random_game_detail',
                           name='random_game_detail'),

                       
                       url(r'^(?P<game_id>\d+)/$',
                           'game_detail',
                           name='game_detail'),

                       )
