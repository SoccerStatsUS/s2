import math

from django import template

register = template.Library()


@register.simple_tag
def team_result_data(team, games):
    l = []
    for game in games:
        t = (game.margin(team), game.date, game.location)
        l.append(t)

    return l


@register.inclusion_tag('templatetags/charts/results.html')
def recent_results_chart(team, games):
    games = list(games)
    if not games:
        return {'bars': []}

    width, height = 960, 198
    left, right, top, half = 32, 16, 22, 58
    baseline = top + half
    plot_width = width - left - right
    slot = plot_width / len(games)
    bar_width = min(26, max(8, slot * .58))

    rows = []
    for game in games:
        if game.team1_id == team.id:
            opponent = game.team2
            goals_for, goals_against = game.team1_score, game.team2_score
            result = game.team1_result
        else:
            opponent = game.team1
            goals_for, goals_against = game.team2_score, game.team1_score
            result = game.team2_result
        rows.append((game, opponent, goals_for, goals_against,
                     goals_for - goals_against, result))

    maximum = max(1, max(abs(row[4]) for row in rows))
    scale = half / maximum
    bars = []
    result_classes = {'w': 'win', 'l': 'loss', 't': 'tie'}
    result_names = {'w': 'win', 'l': 'loss', 't': 'draw'}
    label_every = max(1, math.ceil(70 / slot))
    for index, (game, opponent, goals_for, goals_against, margin, result) in enumerate(rows):
        if result not in result_names:
            result = 'w' if margin > 0 else 'l' if margin < 0 else 't'
        bar_height = abs(margin) * scale
        if margin > 0:
            y = baseline - bar_height
            value_y = y - 5
            value = f'+{margin}'
        elif margin < 0:
            y = baseline
            value_y = y + bar_height + 13
            value = str(margin).replace('-', '\N{MINUS SIGN}')
        else:
            y = baseline - 2
            bar_height = 4
            value_y = baseline - 7
            value = '0'

        x = left + index * slot + (slot - bar_width) / 2
        date_text = f'{game.date.strftime("%b")} {game.date.day}, {game.date.year}'
        bars.append({
            'hit_x': left + index * slot,
            'hit_width': slot,
            'x': x,
            'center': x + bar_width / 2,
            'y': y,
            'width': bar_width,
            'height': bar_height,
            'value_y': value_y,
            'value': value,
            'date': (f'{game.date.month}/{game.date.day}/{str(game.date.year)[2:]}'
                     if (len(rows) - 1 - index) % label_every == 0 else ''),
            'result': result_classes[result],
            'url': game.get_absolute_url(),
            'title': (f'{date_text} vs. {opponent.name}: '
                      f'{goals_for}\N{EN DASH}{goals_against} '
                      f'{result_names[result]} ({value})'),
        })

    count = len(bars)
    return {
        'bars': bars,
        'svg': {
            'width': width,
            'height': height,
            'left': left,
            'right_edge': width - right,
            'top': top,
            'bottom': baseline + half,
            'baseline': baseline,
            'date_y': baseline + half + 28,
        },
        'maximum': maximum,
        'caption': (f'Goal difference in the {count} most recent recorded '
                    f'result{"" if count == 1 else "s"}, oldest to newest'),
    }
