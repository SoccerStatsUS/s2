from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('goals.views', 
                       url(r'^$',
                           'goals_index',
                           name='goals_index'),

                       )
