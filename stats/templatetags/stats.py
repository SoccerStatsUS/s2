from django import template

register = template.Library()

@register.inclusion_tag('templatetags/stats.html')
def stats_table(stats, exclude='', count=None):

    # Can't filter a query once a slice has been taken.
    # The first try might (?) be faster for large, unsliced stats.
    try:
        has_shots = stats.exclude(shots=None).exists()
        has_assists = stats.exclude(assists=None).exists()
        has_minutes = stats.exclude(minutes=None).exists()
        has_games_started = stats.exclude(games_started=None).exists()

    except AssertionError:
        vals = stats.values_list('shots', 'assists', 'minutes', 'games_started')
        has_value = lambda i: set(e[0] for e in vals) != set([None])
        has_shots, has_assists, has_minutes, has_games_started = [has_value(e) for e in range(4)]

    #if stats.filter(games_played=None).exists():
    #    stats = stats.order_by('-games_played')
    #else:
    #    stats = stats.order_by('-minutes')        

    if count:
        stats = stats[:count]

    return {
        'stats': stats,
        'exclude': set(exclude.split(',')),
        'has_shots': has_shots,
        'has_assists': has_assists,
        'has_minutes': has_minutes,
        'has_games_started': has_games_started,
        }
