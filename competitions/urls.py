from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('s2.competitions.views', 
                       url(r'^$',
                           'competition_index',
                           name='competition_index'),

                       url(r'^c/(?P<competition_id>\d+)/$',
                           'competition_detail',
                           name='competition_detail'),

                       url(r'^s/(?P<season_id>\d+)/$',
                           'season_detail',
                           name='season_detail'),


                       )
