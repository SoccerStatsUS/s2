from places import views
from django.urls import path, re_path

urlpatterns = [ 

                       path('', views.country_index,
                           name='country_index'),

                       path('states/', views.state_index,
                           name='state_index'),

                       path('countries/<path:slug>/', views.country_detail,
                           name='country_detail'),


                       path('states/<path:slug>/', views.state_detail,
                           name='state_detail'),

                       path('cities/', views.city_index,
                           name='city_index'),


                       path('cities/<path:slug>/', views.city_detail,
                           name='city_detail'),

                       path('stadiums/', views.stadium_index,
                           name='stadium_index'),


                       re_path(r'^stadiums/(?P<slug>[a-z0-9-]+)/$',                       
                           views.stadium_detail,
                           name='stadium_detail'),

                       re_path(r'^stadiums/(?P<slug>[a-z0-9-]+)/games$',                       
                           views.stadium_games,
                           name='stadium_games'),


]
