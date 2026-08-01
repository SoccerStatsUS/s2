from news import views
from django.urls import path

urlpatterns = [

                       path('', views.news_index,
                           name='news_index'),


]
