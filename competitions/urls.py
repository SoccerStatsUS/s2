from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('s2.competitions.views', 
                       url(r'^$',
                           'competition_index',
                           name='competition_index'),

                       url(r'^(?P<competition_slug>[a-z0-9-]+)/$',
                           'competition_detail',
                           name='competition_detail'),

                       url(r'^(?P<competition_slug>[a-z0-9-]+)/(?P<season_slug>[a-z0-9-]+)/$',
                           'season_detail',
                           name='season_detail'),


                       )
