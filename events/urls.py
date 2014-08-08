from django.conf.urls import patterns, url

urlpatterns = patterns('events.views', 
                       url(r'^$',
                           'event_index',
                           name='event_index'),
                       )
