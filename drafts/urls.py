from drafts import views
from django.urls import path, re_path

urlpatterns = [ 

                       path('', views.drafts_index,
                           name='drafts_index'),

                       re_path(r'^(?P<competition_slug>[a-z0-9-]+)/(?P<draft_slug>[a-z0-9-]+)/(?P<season>[a-z0-9-]+)/$',
                           views.draft_detail,
                           name='draft_detail'),

                       path('bigboard', views.big_board,
                           name='big_board'),

                       re_path(r'^x/(?P<slug>[a-z0-9-]+)',
                           views.draft_person_ajax,
                           name='draft_person_ajax'),


]
