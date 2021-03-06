from django.conf.urls import patterns, url

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

                       url(r'^r/$',
                           'random_person_detail',
                           name='random_person_detail'),
                       

                       url(r'^(?P<slug>[a-z0-9-]+)/$',
                           'person_detail',
                           name='person_detail'),

                       url(r'^id/(?P<pid>\d+)/$',
                           'person_id_detail',
                           name='person_id_detail'),


                       url(r'^(?P<slug>[a-z0-9-]+)/goals/$',
                           'person_detail_goals',
                           name='person_detail_goals'),

                       url(r'^(?P<slug>[a-z0-9-]+)/games/$',
                           'person_detail_games',
                           name='person_detail_games'),

                       url(r'^(?P<slug>[a-z0-9-]+)/referee/$',
                           'person_detail_referee_games',
                           name='person_detail_referee_games'),



                       url(r'^(?P<slug>[a-z0-9-]+)/stats/$',
                           'person_detail_stats',
                           name='person_detail_stats'),


)
