from events import views
from django.urls import path

urlpatterns = [ 
                       path('', views.events_index,
                           name='events_index'),
                       ]
