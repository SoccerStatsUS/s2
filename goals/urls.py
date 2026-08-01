from goals import views
from django.urls import path

urlpatterns = [ 
                       path('', views.goals_index,
                           name='goals_index'),

                       ]
