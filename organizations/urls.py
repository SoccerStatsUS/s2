from django.conf.urls import patterns, url

urlpatterns = patterns('organizations.views', 
                       url(r'^$',
                           'organizations_index',
                           name='organizations_index'),

                       url(r'^confederations/$',
                           'confederations_index',
                           name='confederations_index'),

                       url(r'^(?P<confederation_slug>[a-z0-9-]+)/$',
                           'confederation_detail',
                           name='confederation_detail'),

)
