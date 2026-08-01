from teams import views
from django.urls import path, re_path

urlpatterns = [ 

                       path('', views.team_index,
                           name='team_index'),

                       path('az/<path:fragment>/', views.team_name_fragment,
                           name='team_name_fragment'),
                       
                       path('bad/', views.bad_teams,
                           name='bad_teams'),

                       path('seasons/', views.seasons_dashboard,
                           name='seasons_dashboard'),

                       path('standings/', views.team_standings,
                           name='team_standings'),

                       re_path(r'^(?P<team_slug>[a-z0-9-]+)/(?P<year>\d+)/$',
                           views.team_year_detail,
                           name='team_year_detail'),

                       path('r/', views.random_team_detail,
                           name='random_team_detail'),

                       re_path(r'^(?P<team_slug>[a-z0-9-]+)/$',
                           views.team_detail,
                           name='team_detail'),

                       re_path(r'^(?P<team_slug>[a-z0-9-]+)/stats/$',
                           views.team_stats,
                           name='team_stats'),

                       re_path(r'^(?P<team_slug>[a-z0-9-]+)/picks/$',
                           views.team_picks,
                           name='team_picks'),

                       re_path(r'^(?P<team_slug>[a-z0-9-]+)/draftees/$',
                           views.team_draftees,
                           name='team_draftees'),

                       re_path(r'^(?P<team_slug>[a-z0-9-]+)/games/$',
                           views.team_games,
                           name='team_games'),

                       re_path(r'^(?P<team_slug>[a-z0-9-]+)/graphs/$',
                           views.team_graphs,
                           name='team_graphs'),

                       re_path(r'^(?P<team_slug>[a-z0-9-]+)/calendar/$',
                           views.team_calendar,
                           name='team_calendar'),

                       re_path(r'^(?P<team1_slug>[a-z0-9-]+)/v/(?P<team2_slug>[a-z0-9-]+)/$',
                           views.team_versus,
                           name='team_versus'),

                       re_path(r'^(?P<team_slug>[a-z0-9-]+)/c/(?P<competition_slug>[a-z0-9-]+)/$',
                           views.team_competition_detail,
                           name='team_competition_detail'),

                       re_path(r'^(?P<team_slug>[a-z0-9-]+)/c/(?P<competition_slug>[a-z0-9-]+)/(?P<season_slug>[a-z0-9-]+)/$',
                           views.team_season_detail,
                           name='team_season_detail'),

                       re_path(r'^(?P<team_slug>[a-z0-9-]+)/(?P<position_slug>[a-z0-9-]+)/$',
                           views.team_position_detail,
                           name='team_position_detail'),

                       path('ajax', views.teams_ajax,
                           name='teams_ajax'),



]
