from django.conf.urls import patterns, url

urlpatterns = patterns('stats.views', 

                       url(r'^$',
                           'stats_index',
                           name='stats_index'),

)
