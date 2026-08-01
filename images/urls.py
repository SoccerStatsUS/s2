from images import views
from django.urls import path

urlpatterns = [ 

                       path('<int:image_id>/', views.image_detail,
                           name='image_detail'),


]
