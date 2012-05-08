from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('places.views', 

                       url(r'^$',
                           'country_index',
                           name='country_index'),

                       url(r'^state/$',
                           'state_index',
                           name='state_index'),

                       url(r'^country/(?P<slug>.+)/$',
                           'country_detail',
                           name='country_detail'),

                       url(r'^state/(?P<sid>.+)/$',
                           'state_detail',
                           name='state_detail'),


                       url(r'^city/(?P<cid>.+)/$',
                           'city_detail',
                           name='city_detail'),

                       url(r'^stadium/(?P<slug>[a-z0-9-]+)/$',                       
                           'stadium_detail',
                           name='stadium_detail'),


)
