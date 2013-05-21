from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('videos.views', 

                       url(r'^$',
                           'video_index',
                           name='video_index'),

                       )
