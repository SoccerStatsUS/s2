import os
import pymongo
import sys


from django.core.wsgi import get_wsgi_application
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
application = get_wsgi_application()



from django.db import transaction

from bios.models import Bio
from news.models import NewsSource, FeedItem, archive_id, mentions, name_lookup

connection = pymongo.MongoClient()
soccer_db = connection.soccer

from getters import keep_news_item, make_source_getter

@transaction.atomic
def update_news():
    print("loading news")

    urls = set(list(FeedItem.objects.values_list('url', flat=True)))

    print(len(urls))
    print(soccer_db.news.estimated_document_count())

    source_getter = make_source_getter()
    people = name_lookup(Bio.objects.bio_dict())

    i = 0

    for e in soccer_db.news.find():
        if e['url'] not in urls and keep_news_item(e):
            e.pop('_id')
            text = e.pop('text', '')
            source_id = source_getter(e.pop('source'))
            e['source_id'] = source_id
            e['archive_id'] = archive_id(e['url'])
            item = FeedItem.objects.create(**e)
            item.people.set(mentions('. '.join([e['title'], e['summary'], text]), people))
            i += 1

    print(i)



def update():
    print("updating")
    os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
    update_news()


if __name__ == "__main__":
    if sys.argv[1] == '1':
        update()
