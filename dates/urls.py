from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('s2.dates.views', 

                       url(r'^(?P<year>\d\d\d\d)$',
                           'year_detail',
                           name='year_detail'),

                       url(r'^(?P<year>\d\d\d\d)/(?P<month>\d{1,2})$',
                           'month_detail',
                           name='month_detail'),

                       url(r'^(?P<year>\d\d\d\d)/(?P<month>\d{1,2})/(?P<day>\d{1,2})$',
                           'date_detail',
                           name='date_detail'),


                       )
