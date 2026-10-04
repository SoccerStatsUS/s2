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

    width = 960
    left, right, top, half = 32, 16, 12, 58
    baseline = top + half
    plot_width = width - left - right
    # Bars touch; a short list keeps a readable bar rather than stretching.
    bar_width = min(26, plot_width / len(games))

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
    for index, (game, opponent, goals_for, goals_against, margin, result) in enumerate(rows):
        if result not in result_names:
            result = 'w' if margin > 0 else 'l' if margin < 0 else 't'
        bar_height = abs(margin) * scale
        if margin > 0:
            y = baseline - bar_height
        elif margin < 0:
            y = baseline
        else:
            y = baseline - 2
            bar_height = 4

        if game.date:
            date_text = f'{game.date.strftime("%b")} {game.date.day}, {game.date.year}'
        else:
            date_text = 'Date unknown'
        score = (f'{goals_for}\N{EN DASH}{goals_against} {result_names[result]} '
                 f'vs. {opponent.name}')
        bars.append({
            'x': left + index * bar_width,
            'y': y,
            'width': bar_width,
            'height': bar_height,
            'result': result_classes[result],
            'url': game.get_absolute_url(),
            'tip': f'{score}|{date_text}',
            'label': f'{date_text}: {score}',
        })

    count = len(bars)
    return {
        'bars': bars,
        'svg': {
            'width': width,
            'height': baseline + half + top,
            'left': left,
            'right_edge': width - right,
            'top': top,
            'bottom': baseline + half,
            'baseline': baseline,
            'plot_height': half * 2,
        },
        'maximum': maximum,
        'caption': (f'Goal difference in the {count} '
                    f'result{"" if count == 1 else "s"} listed below, oldest to newest'),
    }
