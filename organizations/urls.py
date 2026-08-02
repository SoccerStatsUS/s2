from organizations import views
from django.urls import path, re_path

urlpatterns = [
                       path('', views.organizations_index,
                           name='organizations_index'),

                       re_path(r'^(?P<confederation_slug>[a-z0-9-]+)/$',
                           views.confederation_detail,
                           name='confederation_detail'),

]
