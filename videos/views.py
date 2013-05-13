import datetime

from django.db.models import Count
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

from videos.models import Video
from games.models import Game

def video_index(request):

    video_games = Game.objects.exclude(video='')
    video_urls = [e[0] for e in video_games.values_list('video')]

    context = {
        #'videos': video_urls,
        'games': video_games,
        }
    return render_to_response("videos/index.html",
                              context,
                              context_instance=RequestContext(request))


