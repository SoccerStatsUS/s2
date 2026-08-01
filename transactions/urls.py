from transactions import views
from django.urls import path

urlpatterns = [ 
                       path('', views.transaction_index,
                           name='transaction_index'),

                       path('<int:transaction_id>/', views.transaction_detail,
                           name='transaction_detail'),


                       ]
