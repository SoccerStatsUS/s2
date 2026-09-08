from sources import views
from django.urls import path

urlpatterns = [ 

                       path('', views.source_index,
                           name='source_index'),

                       path('<slug:source_slug>/', views.source_detail,
                           name='source_detail'),

                       ]
