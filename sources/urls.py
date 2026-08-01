from sources import views
from django.urls import path

urlpatterns = [ 

                       path('', views.source_index,
                           name='source_index'),

                       path('<int:source_id>/', views.source_detail,
                           name='source_detail'),

                       ]
