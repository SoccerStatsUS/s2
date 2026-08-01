from competitions import views
from django.urls import path, re_path

urlpatterns = [ 
                       path('', views.competition_index,
                           name='competition_index'),


                       path('s/names/', views.season_names,
                           name='season_names'),


                       re_path(r'^s/(?P<season_slug>[a-z0-9-]+)/$',
                           views.season_list,
                           name='season_list'),


                       re_path(r'^level/(?P<level_slug>[a-z0-9-]+)/$',
                           views.level_detail,
                           name='level_detail'),


                       path('r/', views.random_competition_detail,
                           name='random_competition_detail'),

                       re_path(r'^(?P<competition_slug>[a-z0-9-]+)/$',
                           views.competition_detail,
                           name='competition_detail'),


                       re_path(r'^(?P<competition_slug>[a-z0-9-]+)/stats/$',
                           views.competition_stats,
                           name='competition_stats'),

                       re_path(r'^(?P<competition_slug>[a-z0-9-]+)/attendance/$',
                           views.competition_attendance,
                           name='competition_attendance'),


                       re_path(r'^(?P<competition_slug>[a-z0-9-]+)/games/$',
                           views.competition_games,
                           name='competition_games'),

                       re_path(r'^(?P<competition_slug>[a-z0-9-]+)/v/(?P<competition2_slug>[a-z0-9-]+)/$',
                           views.competition_vs,
                           name='competition_vs'),


                       re_path(r'^superseason/(?P<superseason_slug>[a-z0-9-]+)/$',
                           views.superseason_detail,
                           name='superseason_detail'),

                       re_path(r'^(?P<competition_slug>[a-z0-9-]+)/(?P<season_slug>[a-z0-9-]+)/$',
                           views.season_detail,
                           name='season_detail'),

                       re_path(r'^(?P<competition_slug>[a-z0-9-]+)/(?P<season_slug>[a-z0-9-]+)/d/(?P<year>\d+)/(?P<month>\d*)/(?P<day>\d*)/$',
                           views.season_date_detail,
                           name='season_date_detail'),


                       re_path(r'^(?P<competition_slug>[a-z0-9-]+)/(?P<season_slug>[a-z0-9-]+)/stats/$',
                           views.season_stats,
                           name='season_stats'),

                       re_path(r'^(?P<competition_slug>[a-z0-9-]+)/(?P<season_slug>[a-z0-9-]+)/games/$',
                           views.season_games,
                           name='season_games'),

                       re_path(r'^(?P<competition_slug>[a-z0-9-]+)/(?P<season_slug>[a-z0-9-]+)/goals/$',
                           views.season_goals,
                           name='season_goals'),

                       re_path(r'^(?P<competition_slug>[a-z0-9-]+)/(?P<season_slug>[a-z0-9-]+)/attendance/$',
                           views.season_attendance,
                           name='season_attendance'),


                       re_path(r'^(?P<competition_slug>[a-z0-9-]+)/(?P<season_slug>[a-z0-9-]+)/salaries/$',
                           views.season_salaries,
                           name='season_salaries'),



                       re_path(r'^(?P<competition_slug>[a-z0-9-]+)/(?P<season_slug>[a-z0-9-]+)/graphs/$',
                           views.season_graphs,
                           name='season_graphs'),


                       ]
