from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('positions.views', 

                       url(r'^$',
                           'index',
                           name='index'),



                       url(r'^managers/$',
                           'manager_index',
                           name='manager_index'),

)
