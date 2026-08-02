from standings import views
from django.urls import path

urlpatterns = [ 

                       path('', views.standings_index,
                           name='standings_index'),

                       path('qa/', views.standings_qa,
                           name='standings_qa'),

]
