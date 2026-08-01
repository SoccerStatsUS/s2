from stats import views
from django.urls import path

urlpatterns = [ 

                       path('', views.stats_index,
                           name='stats_index'),

]
