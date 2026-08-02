from django.contrib import admin
from django.contrib.sitemaps import views as sitemap_views
from django.views.decorators.cache import cache_page
from django.views.generic import RedirectView, TemplateView
from django.urls import include
from django.urls import path

from games import views as games_views
from sitemaps import SITEMAPS


urlpatterns = [
    path('', games_views.homepage, name="home"),

    path('search/', games_views.search, name="search"),

    path('favicon.ico', RedirectView.as_view(url='/static/favicon.svg'), name="favicon"),

    path('sitemap.xml', cache_page(60 * 60 * 12)(sitemap_views.index),
         {'sitemaps': SITEMAPS}, name='sitemap_index'),
    path('sitemap-<section>.xml', cache_page(60 * 60 * 12)(sitemap_views.sitemap),
         {'sitemaps': SITEMAPS}, name='django.contrib.sitemaps.views.sitemap'),

    path('everything/', games_views.everything, name='everything_index'),
    path('more/', RedirectView.as_view(url='/everything/', permanent=True)),

    path('about/', games_views.about, name='about_index'),

    path('awards/', include('awards.urls')),
    path('bios/', include('bios.urls')),
    path('c/', include('competitions.urls')),
    path('contact/', include('contact.urls')),
    path('dates/', include('dates.urls')),
    path('drafts/', include('drafts.urls')),
    path('events/', include('events.urls')),
    path('games/', include('games.urls')),
    path('goals/', include('goals.urls')),
    path('levels/', include('levels.urls')),
    path('lineups/', include('lineups.urls')),
    path('salaries/', include('money.urls')),
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
