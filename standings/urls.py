from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('standings.views', 

                       url(r'^$',
                           'bad_standings',
                           name='bad_standings'),

                       url(r'^bad/$',
                           'bad_standings',
                           name='bad_standings'),

)
