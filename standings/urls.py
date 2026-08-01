from standings import views
from django.urls import path

urlpatterns = [ 

                       path('', views.bad_standings,
                           name='bad_standings'),

                       path('bad/', views.bad_standings,
                           name='bad_standings'),

]
