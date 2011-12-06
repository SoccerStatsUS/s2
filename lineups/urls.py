from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('s2.lineups.views', 
                       url(r'^$',
                           'lineup_index',
                           name='lineup_index'),

                       url(r'^ajax$',
                           'lineup_ajax',
                           name='lineup_ajax'),

)
