from django.conf.urls import patterns, url

urlpatterns = patterns('goals.views', 
                       url(r'^$',
                           'goals_index',
                           name='goals_index'),

                       )
