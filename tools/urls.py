from tools import views
from django.urls import path

urlpatterns = [ 

                       path('', views.tool_index,
                           name='tool_index'),


                       path('games/', views.game_search,
                           name='game_search'),

                       path('stats/', views.stat_search,
                           name='stat_search'),


                       path('goals/', views.goal_search,
                           name='goal_search'),


                       path('lineups/', views.lineup_search,
                           name='lineup_search'),


                       path('ajax/games/', views.games_ajax,
                           name='games_ajax'),

                       path('ajax/gamesid/', views.games_ajax_by_id,
                           name='games_ajax_by_id'),

                       path('ajax/statsid/', views.stats_ajax_by_id,
                           name='stats_ajax_by_id'),


                       path('ajax/stats/', views.stats_ajax,
                           name='stats_ajax'),


                       path('ajax/goals/', views.goals_ajax,
                           name='goals_ajax'),


                       path('ajax/lineups/', views.lineups_ajax,
                           name='lineups_ajax'),




]
