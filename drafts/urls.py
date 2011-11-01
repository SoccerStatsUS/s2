from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('s2.drafts.views', 

                       url(r'^$',
                           'drafts_index',
                           name='drafts_index'),

                       url(r'^(?P<competition_slug>[a-z0-9-]+)/(?P<draft_slug>[a-z0-9-]+)/$',
                           'draft_detail',
                           name='draft_detail'),

)
