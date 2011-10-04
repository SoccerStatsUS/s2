def index(request):
    """A list of all teams in the database."""

    teams = Team.reals.order_by("short_name")
    ctx = {"teams": teams}
    return render_to_response("teams/index.html",
                              ctx,
                              context_instance=RequestContext(request)
                              )

def defunct(request):
    """A list of all teams in the database."""

    teams = Team.defuncts.order_by("short_name")
    ctx = {"teams": teams}
    return render_to_response("teams/index.html",
                              ctx,
                              context_instance=RequestContext(request)
                              )


def team_detail(request, slug):
    team = get_object_or_404(Team, slug=slug)
    years = team.years_with_stats()

    # Whoa whoa whoa what is this stuff?
    minutes = {}
    games = {}
    goals = {}
    assists = {}


    stats = SeasonStat.objects.filter(team=team)
    for stat in stats:
        player = stat.player
        if player not in minutes:
            minutes[player] = games[player] = goals[player] = assists[player] = 0
        minutes[player] += stat.minutes
        games[player] += stat.games_played
        goals[player] += stat.goals
        assists[player] += stat.assists

    sort_leaders = lambda d: sorted(d.items(), key=lambda e: -e[1])

    context = {
        'team': team,
        'years': years,
        "minutes": sort_leaders(minutes)[:10],
        "games": sort_leaders(games)[:10],
        "goals": sort_leaders(goals)[:10],
        "assists": sort_leaders(assists)[:10],
        }

    return render_to_response("teams/team.html",
                              context,
                              context_instance=RequestContext(request)
                              )
    

