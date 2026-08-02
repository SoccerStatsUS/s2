from django.db.models import Count
from django.shortcuts import render, get_object_or_404
from django.template import RequestContext
from django.views.decorators.cache import cache_page

from bios.models import Bio
from competitions.models import Competition, Season
from drafts.models import Draft


@cache_page(60 * 60 * 12)
def drafts_index(request):
    """
    List all drafts.
    """

    drafts = (Draft.objects.exclude(competition=None)
              .select_related('competition', 'season')
              .annotate(pick_count=Count('pick'))
              .order_by('-season__name', 'name'))

    # No draft in the data carries a start date, so the index doesn't offer a
    # date column; pick counts are the figure worth showing instead.
    years = sorted(d.season.name for d in drafts)
    competitions = sorted({d.competition.abbreviation or d.competition.name
                           for d in drafts})

    context = {
        'drafts': drafts,
        'draft_count': len(years),
        'pick_count': sum(d.pick_count for d in drafts),
        'first_year': years[0] if years else None,
        'last_year': years[-1] if years else None,
        'competitions': competitions,
        }
    return render(request, "drafts/index.html",
                              context)


@cache_page(60 * 60 * 12)
def draft_detail(request, competition_slug, draft_slug, season):
    """
    Draft detail page. Don't want to use competition since some drafts don't have a competition?
    """
    competition = get_object_or_404(Competition, slug=competition_slug)
    season = get_object_or_404(Season, competition=competition, name=season)
    draft = get_object_or_404(Draft, season=season, slug=draft_slug, competition=competition)

    context = {
        'draft': draft,
        }
    return render(request, "drafts/detail.html",
                              context)





def big_board(request):
    drafts = Draft.objects.filter(name__contains='USMNT')
    
    context = {
        'drafts': drafts,
        }

    return render(request, 'drafts/bigboard.html',
                              context)


def draft_person_ajax(request, slug):
    context = {
        'player': Bio.objects.get(slug=slug)
        }
    return render(request, 'drafts/ajax.html',
                              context)
