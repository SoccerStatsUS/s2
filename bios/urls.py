from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('bios.views', 
                       url(r'^$',
                           'person_index',
                           name='person_index'),

                       url(r'^az/(?P<fragment>.+)/$',
                           'bio_name_fragment',
                           name='bio_name_fragment'),

                       url(r'^bad/$',
                           'bad_bios',
                           name='bad_bios'),

                       url(r'^oneword/?$',
                           'one_word',
                           name='one_word'),
                       

                       url(r'^(?P<slug>[a-z0-9-]+)/$',
                           'person_detail',
                           name='person_detail'),

                       url(r'^ajax/stats/$',
                           'bio_detail_stats',
                           name='bio_detail_stats'),


)
