from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('s2.stats.views', 

                       url(r'^$',
                           'stats_index',
                           name='stats_index'),

                       url(r'^ajax$',
                           'stats_ajax',
                           name='stats_ajax'),


)
