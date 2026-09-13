"""
The game page's event spine: every recorded event in one chronological list,
home events left, away events right, minute and running score down the middle.

Only goals and substitutions have rows in the database. Cards and fouls are
listed in UNHELD so the page can say they are missing rather than imply a
complete timeline; when a source for them lands, add their events here and
take them out of UNHELD.
"""

from collections import defaultdict

REGULATION = 90

KINDS = ('goals', 'substitutions', 'cards', 'fouls')
UNHELD = ('cards', 'fouls')


def build_spine(game, goals, lineups):
    goals = list(goals)
    placed = [goal_event(g) for g in goals if g.minute is not None]
    unplaced = [goal_event(g) for g in goals if g.minute is None]
    subs = substitution_events(game, lineups)

    show_score, why_not = score_shown(game, goals, unplaced)
    rows = minute_rows(game, placed + subs, show_score)
    rows = with_dividers(game, rows)
    rows.extend({'minute': None, 'score': None, **sided(game, [e])} for e in unplaced)

    present = [k for k, have in (('goals', goals), ('substitutions', subs)) if have]
    missing = [k for k in KINDS if k not in present and k not in UNHELD]

    notes = []
    if unplaced:
        n = len(unplaced)
        notes.append('%d goal%s no recorded minute and %s listed last.' % (
            n, ' has' if n == 1 else 's have', 'is' if n == 1 else 'are'))
    if why_not:
        notes.append(why_not)

    return {
        'rows': rows,
        'show_score': show_score,
        'present': present,
        'missing': missing,
        'unheld': list(UNHELD),
        'notes': notes,
    }


def goal_event(goal):
    if goal.own_goal:
        kind, player = 'own_goal', goal.own_goal_player
    elif goal.penalty:
        kind, player = 'penalty', goal.player
    else:
        kind, player = 'goal', goal.player
    return {
        'kind': kind,
        'minute': goal.minute,
        'team_id': goal.team_id,
        'player': player,
        'assists': [a.player for a in goal.assists()],
    }


def substitution_events(game, lineups):
    """
    One event per team and minute, listing who came on and who went off. The
    record does not say who replaced whom, and several players often change
    at the same minute, so nothing is paired.
    """
    on, off = defaultdict(list), defaultdict(list)
    for a in lineups:
        if a.on:
            on[(a.team_id, a.on)].append(a.player)
        if a.off and a.off != a.on:
            off[(a.team_id, a.off)].append(a.player)

    # An off with nobody coming on is a substitution only before the end of
    # regulation. Finishers carry off = 90 (or the game's length), and that is
    # not an event.
    full = min(REGULATION, game.minutes or REGULATION)
    events = []
    for team_id, minute in sorted(set(on) | set(off), key=lambda k: k[1]):
        if (team_id, minute) not in on and minute >= full:
            continue
        events.append({
            'kind': 'substitution',
            'minute': minute,
            'team_id': team_id,
            'on': on.get((team_id, minute), []),
            'off': off.get((team_id, minute), []),
        })
    return events


def score_shown(game, goals, unplaced):
    """
    The running score is only worth printing when every goal can be placed and
    the goals on record add up to the final score.
    """
    if not goals:
        return False, None
    if unplaced:
        return False, 'Running score not shown.'
    if game.team1_score is None or game.team2_score is None:
        return False, 'Running score not shown: the final score is not on record.'
    total = game.team1_score + game.team2_score
    if len(goals) != total:
        return False, 'Running score not shown: %d goal%s on record against a final score of %d.' % (
            len(goals), '' if len(goals) == 1 else 's', total)
    return True, None


def minute_rows(game, events, show_score):
    by_minute = defaultdict(list)
    for e in events:
        by_minute[e['minute']].append(e)

    order = {'goal': 0, 'penalty': 0, 'own_goal': 0, 'substitution': 1}
    rows = []
    t1 = t2 = 0
    for minute in sorted(by_minute):
        minute_events = sorted(by_minute[minute], key=lambda e: order[e['kind']])
        scored = False
        for e in minute_events:
            if e['kind'] == 'substitution':
                continue
            scored = True
            if e['team_id'] == game.team1_id:
                t1 += 1
            else:
                t2 += 1
        score = '%d–%d' % (t1, t2) if show_score and scored else None
        rows.append({'minute': minute, 'score': score, **sided(game, minute_events)})
    return rows


def sided(game, events):
    home = [e for e in events if e['team_id'] == game.team1_id]
    away = [e for e in events if e['team_id'] != game.team1_id]
    return {'home': home, 'away': away}


def with_dividers(game, rows):
    """
    Half-time between the halves of regulation; full time only when the game
    went to extra time. Stoppage time past 90 in a 90-minute game just sorts
    after 90.
    """
    if not rows:
        return rows
    minutes = game.minutes or REGULATION
    regulation = REGULATION if minutes >= REGULATION else minutes
    breaks = [(regulation // 2, 'half-time')]
    if minutes > REGULATION:
        breaks.append((REGULATION, 'full time'))

    out = []
    pending = list(breaks)
    for row in rows:
        while pending and row['minute'] > pending[0][0]:
            out.append({'divider': pending.pop(0)[1]})
        out.append(row)
    out.extend({'divider': label} for _, label in pending)
    return out
