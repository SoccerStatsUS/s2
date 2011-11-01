from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('s2.dates.views', 

                       url(r'^(?P<year>\d\d\d\d)$',
                           'year_detail',
                           name='year_detail'),

                       url(r'^(?P<year>\d\d\d\d)/(?P<month>\d\d)$',
                           'month_detail',
                           name='month_detail'),

                       url(r'^(?P<year>\d\d\d\d)/(?P<month>\d\d)/(?P<day>\d\d)$',
                           'date_detail',
                           name='date_detail'),


                       )
