from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('contact.views', 

                       url(r'^$',
                           'contact_index',
                           name='contact_index'),

                       url(r'^thanks/$',
                           'contact_thanks',
                           name='contact_thanks'),

)
