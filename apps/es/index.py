# -*- coding:utf-8 -*-
from datetime import datetime, timezone
from elasticsearch_dsl.index import Index

from .models import Article, BlogLive, Danmu, client


IndexDict = {
    'Article': Article,
    'BlogLive': BlogLive,
    'Danmu': Danmu,
}


# create the mappings in elasticsearch
def create_index(index=''):
    if not index:
        return index
    mod = IndexDict.get(index, None)
    if hasattr(mod, 'exists') and hasattr(mod, 'init'):
        return 'mod is exists or init err'
    # if mod.exists():
    #     return 'mod:{} is exists'.format(mod)
    try:
        ret = mod.init()
    except Exception as e:
        return "{}".format(e)

    return 'Create index name:{} ret:{}'.format(index, ret)


def delete_index(index=''):
    if not index:
        return index
    mod = IndexDict.get(index, None)
    if hasattr(mod, 'exists') and hasattr(mod, 'delete'):
        return 'mode exists or delete err'

    try:
        ret = mod._index.delete(ignore=[400, 404])
    except Exception as e:
        return '{}'.format(e)
    return 'Delete index name:{} ret:{}'.format(index, ret)


def ping():
    ret = client.ping()
    return 'ping status:{}'.format(ret)


def health():
    ret = client.cluster.health()
    return 'health status:{}'.format(ret)


def create_data():
    init_test_data()
    return 'create data ok '


def add_article(id_=None, title='', body='', tags=None, published_from=None):
    if id_:
        article = Article(meta={'id': id_}, title=title, tags=tags)
    else:
        article = Article(title=title, tags=tags)
    article.body = body
    article.published_from = published_from if published_from else datetime.now(timezone.utc)
    print(article.published_from, id_)
    # article.save()
    return article


def init_test_data():
    for i in range(1000, 25):
        base = i
        if base % 3 == 0:
            add_article(base+2, 'Python is good!', 'Python is good!', ['python'])
        elif base % 3 == 1:
            add_article(base+3, 'Elasticsearch', 'Distributed, open source search and analytics engine', ['elasticsearch'])
        elif base % 3 == 2:
            add_article(base+4, 'Python very quickly', 'Python very quickly', ['python'])
            add_article(base+5, 'Django', 'Python Web framework', ['python', 'django'])
