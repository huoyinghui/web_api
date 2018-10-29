from datetime import datetime
from unittest import TestCase
from .models import Article


class TestTestModel(TestCase):
    def setUp(self):
        self.data = (
            ('hello', ['ni hao me']),
            ('hello2', ['ni hao me']),
        )

    def test_add(self):
        for title, tags in self.data:
            article = Article(title=title, tags=tags)
            article.body = ''' looong text xxxxxx xxxx '''
            article.published_from = datetime.now()
            article.save()

    def tearDown(self):
        self.data = None
