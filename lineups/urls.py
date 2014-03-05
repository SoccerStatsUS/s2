from django.conf.urls import patterns, url

urlpatterns = patterns('lineups.views', 
                       url(r'^$',
                           'lineup_index',
                           name='lineup_index'),

                       url(r'^ajax$',
                           'lineup_ajax',
                           name='lineup_ajax'),

)
