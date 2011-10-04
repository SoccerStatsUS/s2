from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('s2.goals.views', 
                       url(r'^$',
                           'goals_index',
                           name='goals_index'),

                       )
