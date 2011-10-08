import datetime
import difflib

from s2.bios.models import Bio

# http://wiki.python.org/moin/PythonDecoratorLibrary#Memoize

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
        
