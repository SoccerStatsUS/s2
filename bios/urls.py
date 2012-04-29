from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('bios.views', 
                       url(r'^$',
                           'person_index',
                           name='person_index'),

                       url(r'^az/(?P<fragment>.+)/$',
                           'name_fragment',
                           name='name_fragment'),

                       url(r'^bad$',
                           'bad_bios',
                           name='bad_bios'),

                       url(r'^oneword$',
                           'one_word',
                           name='one_word'),
                       

                       url(r'^(?P<slug>[a-z0-9-]+)',
                           'person_detail',
                           name='person_detail'),

)
