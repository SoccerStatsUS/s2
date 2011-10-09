from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('s2.bios.views', 
                       url(r'^$',
                           'person_index',
                           name='person_index'),

                       url(r'^bad$',
                           'bad_bios',
                           name='bad_bios'),
                       

                       url(r'^(?P<slug>[a-z0-9-]+)',
                           'person_detail',
                           name='person_detail'),

)
