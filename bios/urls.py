from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('s2.bios.views', 
                       url(r'^$',
                           'person_index',
                           name='person_index'),


                       url(r"^n/(?P<bio_id>.*)/$",
                           "person_detail",
                           name="person_detail"),
)
