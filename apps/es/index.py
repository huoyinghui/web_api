# -*- coding:utf-8 -*-
from datetime import datetime

from .models import Article, client


# create the mappings in elasticsearch
def create_index():
    ret = Article.init()
    return 'Create index:{}'.format(ret)


def ping():
    ret = client.ping()
    return 'ping status:{}'.format(ret)


def health():
    ret = client.cluster.health()
    return 'health status:{}'.format(ret)


def create_data():
    init_test_data()
    return 'create data ok '


def add_article(id_, title, body, tags):
    article = Article(meta={'id': id_}, title=title, tags=tags)
    article.body = body
    article.published_from = datetime.now()
    article.save()


def init_test_data():
    add_article(2, 'Python is good!', 'Python is good!', ['python'])
    add_article(3, 'Elasticsearch', 'Distributed, open source search and analytics engine', ['elasticsearch'])
    add_article(4, 'Python very quickly', 'Python very quickly', ['python'])
    add_article(5, 'Django', 'Python Web framework', ['python', 'django'])
