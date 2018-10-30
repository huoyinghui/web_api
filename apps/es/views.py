from datetime import datetime

from django.shortcuts import render
from django.http import JsonResponse

# Create your views here.
from django.views.generic.base import View
from .models import Article


class ArticleView(View):
    """

    """

    def get(self, request):
        id = request.GET.get('id', '1ycQwGYBt6UyLsIJXdre')
        article = Article.get(id=id)
        ret = {'data': article}
        if article:
            ret = article.to_dict()
        return JsonResponse(ret)

    def post(self, request):
        title = request.POST.get("title", "")
        tags = request.POST.get("tags", [])
        i = 5
        article = Article(title=title, tags=tags)
        article.body = ''' looong text xxxxxx xxxx_{}'''.format(i)
        article.published_from = datetime.now()
        ret = article.save()
        return JsonResponse({'data': "create blog:{}".format(ret)})
