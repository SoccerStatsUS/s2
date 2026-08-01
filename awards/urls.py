from awards import views
from django.urls import path

urlpatterns = [ 
                       path('', views.award_index,
                           name='award_index'),

                       path('<int:award_id>/', views.award_detail,
                           name='award_detail'),

]
