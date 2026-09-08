from awards import views
from django.urls import path

urlpatterns = [
                       path('', views.award_index,
                           name='award_index'),

                       path('<slug:competition_slug>/<slug:award_slug>/', views.award_detail,
                           name='award_detail'),

                       # The Hall of Fame belongs to no competition, so it has
                       # nothing to sit under.
                       path('<slug:award_slug>/', views.award_detail,
                           name='award_detail_open'),

]
