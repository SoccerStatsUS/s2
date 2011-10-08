from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('s2.dates.views', 
                       url(r'^(?P<year>\d\d\d\d)/(?P<month>\d\d)/(?P<day>\d\d)$',
                           'date_scoreboard',
                           name='date_coreboard'),


                       )
