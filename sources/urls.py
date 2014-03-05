from django.conf.urls import patterns, url

urlpatterns = patterns('sources.views', 

                       url(r'^$',
                           'source_index',
                           name='source_index'),

                       url(r'^(?P<source_id>\d+)/$',
                           'source_detail',
                           name='source_detail'),

                       )
