from videos import views
from django.urls import path

urlpatterns = [ 

                       path('', views.video_index,
                           name='video_index'),

                       ]
