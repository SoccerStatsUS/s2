from django.conf.urls import patterns, url

urlpatterns = patterns('events.views', 
                       url(r'^$',
                           'events_index',
                           name='events_index'),
                       )
