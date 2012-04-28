import datetime
import difflib
import time                                                

from django.db import connection, transaction

# http://wiki.python.org/moin/PythonDecoratorLibrary#Memoize

from bios.models import Bio



def timer(method):

    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()

        print '%r (%r, %r) %2.2f sec' % \
              (method.__name__, args, kw, te-ts)
        return result

    return timed



def insert_sql_pg(table, dict_list):
   # SQLITE does not support multiple row insertion?
    
    formatter = lambda l: "(%s)" % ",".join(["'%s'" % unicode(e) for e in l])
    fields = dict_list[0].keys()
    make_values = lambda d: "%s" % formatter([d[field] for field in fields])
    values = [make_values(e) for e in dict_list]
    value_string = ", ".join([unicode(e) for e in  values])
    sql = "INSERT INTO %s %s VALUES %s;" % (table, formatter(fields), value_string)
    cursor = connection.cursor()
    return cursor.execute(sql)


def insert_sql(table, dict_list):
    if len(dict_list) == 0:
        return
    elif len(dict_list) > 1:
        for d in dict_list:
            insert_sql(table, [d])


    else:
        def formatter(l):
            l2 = []
            for e in l:
                if e == None:
                    l2.append("NULL")
                else:
                    l2.append("'%s'" % unicode(e))
            return "(%s)" % ",".join(l2)
            
        fields = dict_list[0].keys()
        make_values = lambda d: "%s" % formatter([d[field] for field in fields])
        values = [make_values(e) for e in dict_list]
        value_string = ", ".join([unicode(e) for e in  values])
        sql = "INSERT INTO %s %s VALUES %s;" % (table, formatter(fields), value_string)
        cursor = connection.cursor()
        return cursor.execute(sql)


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
        
