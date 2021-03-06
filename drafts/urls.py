from django.conf.urls import patterns, url

urlpatterns = patterns('drafts.views', 

                       url(r'^$',
                           'drafts_index',
                           name='drafts_index'),

                       url(r'^(?P<competition_slug>[a-z0-9-]+)/(?P<draft_slug>[a-z0-9-]+)/(?P<season>[a-z0-9-]+)/$',
                           'draft_detail',
                           name='draft_detail'),

                       url('^bigboard$',
                           'big_board',
                           name='big_board'),

                       url(r'^x/(?P<slug>[a-z0-9-]+)',
                           'draft_person_ajax',
                           name='draft_person_ajax'),


)
