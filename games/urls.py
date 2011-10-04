from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('s2.games.views', 
                       url(r'^$',
                           'games_index',
                           name='games_index'),

                       url(r'^game/(?P<game_id>\d+)/$',
                           'game_detail',
                           name='game_detail'),

                       )
