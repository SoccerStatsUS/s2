import os
import pymongo
import sys

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'


from django.db import transaction

from news.models import NewsSource, FeedItem

connection = pymongo.Connection()
soccer_db = connection.soccer

from getters import make_source_getter

@transaction.commit_on_success
def update_news():
    print("loading news")

    urls = set(list(FeedItem.objects.values_list('url', flat=True)))

    print(len(urls))
    print(soccer_db.news.count())

    source_getter = make_source_getter()

    i = 0

    for e in soccer_db.news.find():
        #if e['dt'] > datetime.datetime(2013, 8, 4):
        #    print(e)


        if e['url'] not in urls:
            e.pop('_id')
            source_id = source_getter(e.pop('source'))
            e['source_id'] = source_id
            FeedItem.objects.create(**e)
            i += 1

    print(i)



def update():
    print("updating")
    os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
    update_news()


if __name__ == "__main__":
    if sys.argv[1] == '1':
        update()
