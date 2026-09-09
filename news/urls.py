from news import views
from django.urls import path

urlpatterns = [
    path('', views.news_index, name='news_index'),
    path('<int:item_id>/', views.news_detail, name='news_detail'),
]
