from money import views
from django.urls import path

urlpatterns = [ 

                       path('', views.money_index,
                           name='money_index'),

                       path('bad/', views.bad_money_index,
                           name='bad_money_index'),

]
