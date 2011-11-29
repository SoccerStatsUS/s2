from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('s2.dates.views', 

                       url(r'^(?P<year>\d+)$',
                           'year_detail',
                           name='year_detail'),

                       url(r'^(?P<year>\d+)/(?P<month>\d+)$',
                           'month_detail',
                           name='month_detail'),

                       url(r'^(?P<year>\d+)/(?P<month>\d+)/(?P<day>\d+)$',
                           'date_detail',
                           name='date_detail'),


                       )
