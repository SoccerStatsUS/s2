from django.conf.urls import patterns, url

urlpatterns = patterns('graphs.views', 

                       url(r'^$',
                           'graphs_index',
                           name='graphs_index'),


                       url(r'^bias/$',
                           'age_bias_graph',
                           name='age_bias_graph'),




                       url(r'^map/$',
                           'map_graph',
                           name='map_graph'),


)
