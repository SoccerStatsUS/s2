import datetime
import difflib

from s2.bios.models import Bio


# http://stackoverflow.com/questions/682367/good-python-modules-for-fuzzy-string-comparison
# Run this as a cron job and store in a database?
# Takes a while.

def get_similar_names(score=.9):

    l = []

    names = sorted([e.name for e in Bio.objects.all()])

    for i, name in enumerate(names):
        for e in names[i+1:]:
            score = difflib.SequenceMatcher(None, name, e).ratio()
            t = (name, e, score)
            #l.append(t)
            if score > .8:
                print datetime.datetime.now()
                print t

    return sorted(l, key=lambda e: e[2])
        
