# -*- coding:utf-8 -*-
from django.urls import path
from .views import ArticleView


app_name = "es"

urlpatterns = [
    path('', ArticleView.as_view(), name="blog"),
]