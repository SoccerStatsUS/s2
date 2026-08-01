from graphs import views
from django.urls import path

urlpatterns = [ 

                       path('', views.graphs_index,
                           name='graphs_index'),


                       path('bias/', views.age_bias_graph,
                           name='age_bias_graph'),




                       path('map/', views.map_graph,
                           name='map_graph'),


]
