from lineups import views
from django.urls import path

urlpatterns = [ 
                       path('', views.lineup_index,
                           name='lineup_index'),

                       path('ajax', views.lineup_ajax,
                           name='lineup_ajax'),

]
