from datetime import datetime
from unittest import TestCase
from django.http import HttpRequest
from .models import Article
from .views import ArticleView



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

    # def test_view_get(self):
    #     request = HttpRequest()
    #     request.GET.setlist('tags', ['hello', 'world'])
    #     request.GET.setdefault('title', 'hello')
    #     request.GET.setdefault('id', 'EyfMv2YBt6UyLsIJjssO')
    #     article = ArticleView()
    #     resp = article.get(request=request)
    #     assert resp.status_code == 200
    #     print(resp.content)

    def test_view_post(self):
        request = HttpRequest()
        request.POST.setlist('tags', ['hello', 'world'])
        request.POST.setdefault('title', 'hello')
        article = ArticleView()
        resp = article.post(request=request)
        assert resp.status_code == 200
        print(resp.content)

    def tearDown(self):
        self.data = None
