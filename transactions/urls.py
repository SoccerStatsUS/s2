from django.conf.urls import patterns, url

urlpatterns = patterns('transactions.views', 
                       url(r'^$',
                           'transaction_index',
                           name='transaction_index'),

                       url(r'^(?P<transaction_id>\d+)/$',
                           'transaction_detail',
                           name='transaction_detail'),


                       )
