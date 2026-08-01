from levels import views
from django.urls import path, re_path

urlpatterns = [ 
                       path('', views.level_index,
                           name='level_index'),

                       re_path(r'^(?P<country_slug>[a-z0-9-]+)/(?P<level>[0-9]+)/$',
                           views.level_detail,
                           name='level_detail'),
]
