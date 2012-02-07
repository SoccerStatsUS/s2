from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('places.views', 

                       url(r'^$',
                           'country_index',
                           name='country_index'),

                       url(r'^(?P<slug>.+)/$',
                           'country_detail',
                           name='country_detail'),

)
