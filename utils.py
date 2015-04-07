import os
import sys

from django.core.wsgi import get_wsgi_application
os.environ['DJANGO_SETTINGS_MODULE'] = 'build_settings'
application = get_wsgi_application()


from collections import defaultdict

import datetime
import difflib
import re
import time                                                

from django.db import connection, transaction

# http://wiki.python.org/moin/PythonDecoratorLibrary#Memoize

from bios.models import Bio


def check_competition_teams(competition, country):
    teams = set()
    errant_teams = set()

    for game in competition.game_set.all():
        teams.add(game.team1)
        teams.add(game.team2)

    for standing in competition.standing_set.all():
        teams.add(standing.team)

    for team in teams:
        if team.city and team.city.country and team.city.country != country:
            errant_teams.add(team)

    return errant_teams
        

def search_for_data(o):
    for item in dir(o):
        if 'set' in item:
            p = getattr(o, item)
            try:
                print(item, p())
            except:
                try:
                    print(item, p.all())
                except:
                    print("fail on {}".format(item))


def find_duplicate_slugs(model):
    d = defaultdict(int)
    for e in model.objects.all():
        d[e.slug] += 1
    return [e[0] for e in d.items() if e[1] > 1]


def timer(method):

    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()

        print('%r (%r, %r) %2.2f sec' % \
              (method.__name__, args, kw, te-ts))
        return result

    return timed


def insert_sql(table, dict_list):
    """
    Insert a list of dicts representing values into a table.
    """

    if not dict_list:
        return

    # Names of fields
    fields = dict_list[0].keys()
    field_string = "%s" % ", ".join(['"%s"' % e for e in fields])

    # Placeholders for values.
    values = [list(e.values()) for e in dict_list]
    value_string = ', '.join(['%s'] * len(values[0]))

    cursor = connection.cursor()
    command = "INSERT INTO {} ({}) VALUES ({});".format(table, field_string, value_string)
    cursor.executemany(command, values)


# This should be eliminated. Replace with functools.lru_cache

class memoized(object):
    """
    Decorator that caches a function's return value each time it is called.
    If called later with the same arguments, the cached value is returned, and
    not re-evaluated.
    """

    def __init__(self, func):
        self.func = func
        self.cache = {}

    def __call__(self, *args):
        try:
            return self.cache[args]
        except KeyError:
            value = self.func(*args)
            self.cache[args] = value
            return value
        except TypeError:
            # uncachable -- for instance, passing a list as an argument.
            # Better to not cache than to blow up entirely.
            return self.func(*args)

    def __repr__(self):
        """Return the function's docstring."""
        return self.func.__doc__

    def __get__(self, obj, objtype):
        """Support instance methods."""
        return functools.partial(self.__call__, obj)



# http://stackoverflow.com/questions/682367/good-python-modules-for-fuzzy-string-comparison
# Run this as a cron job and store in a database?
# Takes a while.


def remove_parentheses(name):
    r = re.match('(.*?)(\(.*?\))(.*)', name)
    if r:
        first, middle, last = [e.strip() for e in r.groups()]
        return '{} {}'.format(first, last)
    else:
        return name

def replace_with_parentheses(name):
    r = re.match('(.*?)\((.*?)\)(.*)', name)
    if r:
        first, middle, last = [e.strip() for e in r.groups()]
        return '{} {}'.format(middle, last)
    else:
        return name


def find_parenthetical_names(qs=None):
    if qs is None:
        qs = Bio.objects.all()

    names = set([e.name for e in qs])

    for e in names:
        n1 = remove_parentheses(e)
        n2 = replace_with_parentheses(e)

        if n1 != e and n1 in names:
            print("'{}': '{}'".format(e, n1))
            
        if n2 != e and n2 in names:
            print("'{}': '{}'".format(e, n2))


def remove_middle_initial(name):
    r = re.match('(\w*?) \w\.? (\w*)', name)
    if r:
        first, last = [e.strip() for e in r.groups()]
        return '{} {}'.format(first, last)
    else:
        return name


def find_middle_initial_names(qs=None):
    if qs is None:
        qs = Bio.objects.all()

    names = set([e.name for e in qs])

    for e in names:
        n1 = remove_middle_initial(e)

        if n1 != e and n1 in names:
            print("'{}': '{}',".format(e, n1))


def find_similar_names(qs=None, threshold=.85):

    f = open('/home/chris/www/sdev/similar', 'w')

    if qs is None:
        qs = Bio.objects.all()

    names = sorted([e.name for e in qs])

    l = []

    for i, name in enumerate(names):
        #print("Processing %s" % name)
        for e in names[i+1:]:
            nscore = difflib.SequenceMatcher(None, name, e).ratio()
            nscores = str(nscore)[:4]
            t = (name, e, nscores)
            #l.append(t)
            if nscore > threshold:
                l.append(t)
                #f.write(str(t))
                #f.write('\n')

    #f.close()

    return sorted(l, key=lambda e: e[2])
        
if __name__ == "__main__":
    pass
