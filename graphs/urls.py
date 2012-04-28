from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('graphs.views', 

                       url(r'^$',
                           'graphs_index',
                           name='graphs_index'),


)
