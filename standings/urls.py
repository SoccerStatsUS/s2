from standings import views
from django.urls import path

urlpatterns = [ 

                       path('', views.standings_index,
                           name='standings_index'),

                       path('bad/', views.bad_standings,
                           name='bad_standings'),

]
