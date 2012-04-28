from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('games.views', 
                       url(r'^$',
                           'games_index',
                           name='games_index'),

                       url(r'^bad$',
                           'bad_games',
                           name='bad_games'),

                       url(r'^(?P<game_id>\d+)/$',
                           'game_detail',
                           name='game_detail'),

                       )
