from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('s2.positions.views', 

                       url(r'^$',
                           'manager_index',
                           name='manager_index'),

)
