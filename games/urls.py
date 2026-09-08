from games import views
from django.urls import path

urlpatterns = [ 
                       path('', views.games_index,
                           name='games_index'),

                       path('qa/', views.games_qa,
                           name='games_qa'),


                       path('r/', views.random_game_detail,
                           name='random_game_detail'),

                       
                       path('<slug:date_slug>/<slug:competition_slug>/<slug:teams_slug>/',
                           views.game_detail,
                           name='game_detail'),

                       ]
