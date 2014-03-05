from django.conf.urls import patterns, url

urlpatterns = patterns('videos.views', 

                       url(r'^$',
                           'video_index',
                           name='video_index'),

                       )
