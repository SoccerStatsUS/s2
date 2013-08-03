from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('images.views', 

                       url(r'^(?P<image_id>\d+)/$',
                           'image_detail',
                           name='image_detail'),


)
