from django.contrib import admin
from django.views.generic import RedirectView, TemplateView
from django.urls import include
from django.urls import path

from dates import views as dates_views
from games import views as games_views


urlpatterns = [
    path('', games_views.homepage, name="home"),

    path('search/', games_views.search, name="search"),

    path('favicon.ico', RedirectView.as_view(url='/static/favicon.svg'), name="favicon"),

    path('about/', TemplateView.as_view(template_name='about/index.html'), name='about_index'),
    path('about/news/', TemplateView.as_view(template_name='about/news.html'), name='about_news'),
    path('about/build/', TemplateView.as_view(template_name='about/build.html'), name='about_build'),

    path('calendar/', dates_views.calendar, name="calendar_index"),
    path('awards/', include('awards.urls')),
    path('bios/', include('bios.urls')),
    path('c/', include('competitions.urls')),
    path('contact/', include('contact.urls')),
    path('dates/', include('dates.urls')),
    path('drafts/', include('drafts.urls')),
    path('events/', include('events.urls')),
    path('games/', include('games.urls')),
    path('goals/', include('goals.urls')),
    path('graphs/', include('graphs.urls')),
    path('levels/', include('levels.urls')),
    path('lineups/', include('lineups.urls')),
    path('money/', include('money.urls')),
    path('news/', include('news.urls')),
    path('organizations/', include('organizations.urls')),
    path('positions/', include('positions.urls')),
    path('places/', include('places.urls')),
    path('sources/', include('sources.urls')),
    path('standings/', include('standings.urls')),
    path('stats/', include('stats.urls')),
    path('teams/', include('teams.urls')),
    path('transactions/', include('transactions.urls')),
    path('videos/', include('videos.urls')),

    path('admin/', admin.site.urls),
]
