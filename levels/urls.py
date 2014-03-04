from django.conf.urls import patterns, url

urlpatterns = patterns('levels.views', 
                       url(r'^$',
                           'level_index',
                           name='level_index'),

                       url(r'^(?P<country_slug>[a-z0-9-]+)/(?P<level>[0-9]+)/$',
                           'level_detail',
                           name='level_detail'),
)
