from positions import views
from django.urls import path, re_path

urlpatterns = [ 

                       path('', views.index,
                           name='index'),

                       re_path(r'^(?P<slug>[a-z0-9-]+)/$',
                           views.position_detail,
                           name='position_detail'),

                       path('managers/', views.manager_index,
                           name='manager_index'),

]
