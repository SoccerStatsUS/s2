from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('positions.views', 

                       url(r'^$',
                           'manager_index',
                           name='manager_index'),

)
