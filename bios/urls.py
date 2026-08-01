from bios import views
from django.urls import path, re_path

urlpatterns = [ 
                       path('', views.person_index,
                           name='person_index'),

                       path('az/<path:fragment>/', views.bio_name_fragment,
                           name='bio_name_fragment'),

                       path('bad/', views.bad_bios,
                           name='bad_bios'),

                       re_path(r'^oneword/?$',
                           views.one_word,
                           name='one_word'),

                       path('r/', views.random_person_detail,
                           name='random_person_detail'),
                       

                       re_path(r'^(?P<slug>[a-z0-9-]+)/$',
                           views.person_detail,
                           name='person_detail'),

                       path('id/<int:pid>/', views.person_id_detail,
                           name='person_id_detail'),


                       re_path(r'^(?P<slug>[a-z0-9-]+)/goals/$',
                           views.person_detail_goals,
                           name='person_detail_goals'),

                       re_path(r'^(?P<slug>[a-z0-9-]+)/games/$',
                           views.person_detail_games,
                           name='person_detail_games'),

                       re_path(r'^(?P<slug>[a-z0-9-]+)/referee/$',
                           views.person_detail_referee_games,
                           name='person_detail_referee_games'),



                       re_path(r'^(?P<slug>[a-z0-9-]+)/stats/$',
                           views.person_detail_stats,
                           name='person_detail_stats'),


]
