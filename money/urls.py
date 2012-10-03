from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('money.views', 

                       url(r'^$',
                           'money_index',
                           name='money_index'),

                       url(r'^bad/$',
                           'bad_money_index',
                           name='bad_money_index'),

)
