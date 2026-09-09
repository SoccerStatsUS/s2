import hashlib
import re
import unicodedata

from django.db import models
from django.urls import reverse

from sources.models import Source

# Going to have to figure out how to save these while rebuilding the database.
# Probably keep a separate database for persistent / non-built data.


class NewsSource(models.Model):
    """
    Probably a blog.
    """    
    # Use djangoproject.com's feed aggregator to build this.
    #? http://github.com/miracle2k/feedplatform 
    # http://birdhouse.org/blog/2009/10/20/generating-rss-mashups-from-django/


    name = models.CharField(max_length=1023)
    url = models.CharField(max_length=1023) 
    feed_url = models.CharField(max_length=1023) 

    # tags = models.ManyToManyField?



    def __str__(self):
        return self.name

    class Meta:
        pass




def archive_id(url):
    """
    The oneonta archive's item id: the first twelve hex digits of the url's SHA-1.
    Computed here too so a rebuild can't change a story's address.
    """
    return hashlib.sha1(url.encode()).hexdigest()[:12]


# The longest name a mention can span, in words.
NAME_WORDS = 5


def words(text):
    """
    Lowercase words with diacritics stripped and punctuation dropped, so a
    name and a mention of it fold the same way: Martínez, O'Brien and a
    possessive O'Brien's included.
    """
    text = unicodedata.normalize('NFKD', text.casefold())
    text = ''.join(c for c in text if not unicodedata.combining(c))
    text = re.sub(r"['’]s\b", '', text).replace("'", '').replace('’', '')
    return re.findall(r'[a-z0-9]+', text)


def is_name_word(word):
    """
    A word of a name has a letter and is at least two characters. That keeps out
    the scores and stray initials filed as people ("1-1.", "S. Day").
    """
    return len(word) > 1 and not word.isdigit()


def name_lookup(names):
    """
    {name: id} -> {word tuple: id}, multi-word names only. A single word
    (Donovan, Pele) would match far too much.
    """
    lookup = {}
    for name, pk in names.items():
        key = tuple(words(name))
        if 1 < len(key) <= NAME_WORDS and all(is_name_word(w) for w in key):
            lookup.setdefault(key, pk)
    return lookup


def mentions(text, lookup):
    """
    Ids of the people named in text, in order of first mention. The longest
    name at a position wins, so a name inside a longer one doesn't fire too.
    """
    ws = words(text)
    found = []
    i = 0
    while i < len(ws):
        for n in range(NAME_WORDS, 1, -1):
            pk = lookup.get(tuple(ws[i:i + n]))
            if pk is not None:
                if pk not in found:
                    found.append(pk)
                i += n
                break
        else:
            i += 1
    return found


class FeedItem(models.Model):
    """
    A single rss item.
    """

    archive_id = models.CharField(max_length=12, unique=True)
    title = models.CharField(max_length=1023)
    dt = models.DateTimeField()
    summary = models.CharField(max_length=1023) 
    url = models.CharField(max_length=1023) 
    source = models.ForeignKey(Source, on_delete=models.CASCADE)
    people = models.ManyToManyField('bios.Bio', related_name='news')

    def time(self):
        return self.dt.strftime("%I:%M %p")

    def get_absolute_url(self):
        return reverse('news_detail', args=[self.archive_id])

    class Meta:
        pass
