from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('places.views', 

                       url(r'^$',
                           'country_index',
                           name='country_index'),

                       url(r'^states/$',
                           'state_index',
                           name='state_index'),

                       url(r'^countries/(?P<slug>.+)/$',
                           'country_detail',
                           name='country_detail'),


                       url(r'^states/(?P<slug>.+)/$',
                           'state_detail',
                           name='state_detail'),

                       url(r'^cities/$',
                           'city_index',
                           name='city_index'),


                       url(r'^cities/(?P<slug>.+)/$',
                           'city_detail',
                           name='city_detail'),

                       url(r'^stadiums/$',
                           'stadium_index',
                           name='stadium_index'),


                       url(r'^stadiums/(?P<slug>[a-z0-9-]+)/$',                       
                           'stadium_detail',
                           name='stadium_detail'),


)
