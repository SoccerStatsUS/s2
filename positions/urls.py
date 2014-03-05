from django.conf.urls import patterns, url

urlpatterns = patterns('positions.views', 

                       url(r'^$',
                           'index',
                           name='index'),

                       url(r'^(?P<slug>[a-z0-9-]+)/$',
                           'position_detail',
                           name='position_detail'),

                       url(r'^managers/$',
                           'manager_index',
                           name='manager_index'),

)
