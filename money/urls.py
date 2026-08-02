from money import views
from django.urls import path

urlpatterns = [ 

                       path('', views.salaries_index,
                           name='salaries_index'),

]
