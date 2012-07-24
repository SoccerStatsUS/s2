from django import template

register = template.Library()

@register.simple_tag
def team_result_data(team, games):
    l = []
    for game in games:
        t = (game.margin(team), game.date, game.location)
        l.append(t)

    return l



