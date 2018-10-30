from datetime import datetime
from unittest import TestCase
from django.http import HttpRequest
from .models import Article, add_article


class TestArticleModel(TestCase):
    def setUp(self):
        self.data = (
            ('hello', ['ni hao me']),
            ('hello2', ['ni hao me']),
        )
        self.ids = [
            'nyduwGYBt6UyLsIJHvAf',
            'iidtwGYBt6UyLsIJq_CJ',
            'hydxwGYBt6UyLsIJz_GU',
        ]

    def init_test_data(self):
        pass

    def test_add(self):
        id = 0
        for title, tags in self.data:
            article = Article(meta={'id': self.ids[id]}, title=title, tags=tags)
            article.body = ''' looong text xxxxxx xxxx '''
            article.published_from = datetime.now()
            article.save()
            id += 1

        for i in range(2):
            article = Article.get(id=self.ids[i])
            assert article.title == self.data[i][0]
            assert article.tags == self.data[i][1]

    def test_mget(self):
        ret = Article.mget(self.ids)
        assert len(ret) == len(self.ids)

    def test_search_body(self):
        assert 1 == 1

    def tearDown(self):
        self.data = None
