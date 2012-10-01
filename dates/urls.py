from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('dates.views', 

                       url(r'^$',
                           'dates_index',
                           name='dates_index'),


                       url('^today/$',
                           'scoreboard_today',
                           name='scoreboard_today'),

                       url(r'^(?P<year>\d+)/$',
                           'year_detail',
                           name='year_detail'),

                       url(r'^(?P<year>\d+)/(?P<month>\d*)/$',
                           'month_detail',
                           name='month_detail'),

                       url(r'^(?P<year>\d+)/(?P<month>\d*)/(?P<day>\d*)/$',
                           'date_detail',
                           name='date_detail'),

                       url(r'^day/(?P<month>\d+)/(?P<day>\d+)/$',
                           'day_detail',
                           name='day_detail'),


                       )
