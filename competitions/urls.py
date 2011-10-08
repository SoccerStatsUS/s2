from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('s2.competition.views', 
                       url(r'^$',
                           'competition_index',
                           name='competition_index'),

                       url(r'^game/(?P<competition_id>\d+)/$',
                           'competition_detail',
                           name='competition_detail'),

                       url(r'^game/(?P<season_id>\d+)/$',
                           'season_detail',
                           name='season_detail'),


                       )
