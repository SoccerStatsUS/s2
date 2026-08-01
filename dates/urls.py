from dates import views
from django.urls import path, re_path

urlpatterns = [ 

                       path('', views.dates_index,
                           name='dates_index'),


                       path('today/', views.scoreboard_today,
                           name='scoreboard_today'),

                       path('<int:year>/', views.year_detail,
                           name='year_detail'),

                       re_path(r'^(?P<year>\d+)/(?P<month>\d*)/$',
                           views.month_detail,
                           name='month_detail'),

                       re_path(r'^(?P<year>\d+)/(?P<month>\d*)/(?P<day>\d*)/$',
                           views.date_detail,
                           name='date_detail'),

                       path('day/<int:month>/<int:day>/', views.day_detail,
                           name='day_detail'),


                       ]
