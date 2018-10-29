# -*- coding:utf-8 -*-
from unittest import TestCase
from .models import TestModel


class TestTestModel(TestCase):
    def setUp(self):
        self.data = {
            'ls': """import os\r\nprint(os.listdir())""",
            'pwd': """import os\r\nprint(os.getcwd())""",
            'hello world': """print('Hello world')"""
        }

    def test_add(self):
        for name, code in self.data.items():
            TestModel.objects.create(name=name, code=code)
        cnt = TestModel.objects.all().count()
        assert cnt == len(self.data)

    def tearDown(self):
        self.data = None
