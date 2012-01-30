from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('places.views', 

                       url(r'^$',
                           'place_index',
                           name='place_index'),

                       url(r'^(?P<name>.+)/$',
                           'place_detail',
                           name='place_detail'),

)
