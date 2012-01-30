from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('awards.views', 
                       url(r'^$',
                           'award_index',
                           name='award_index'),

                       url(r'^(?P<award_id>\d+)/$',
                           'award_detail',
                           name='award_detail'),

)
