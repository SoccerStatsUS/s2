from contact import views
from django.urls import path

urlpatterns = [ 

                       path('', views.contact_index,
                           name='contact_index'),

                       path('thanks/', views.contact_thanks,
                           name='contact_thanks'),

]
