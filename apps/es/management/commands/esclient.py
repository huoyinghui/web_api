from django.core.management.base import BaseCommand
from es.index import ping, create_index, health, create_data, IndexDict, delete_index


class Command(BaseCommand):
    WHICH_CHOICES = [
        health,
        ping, 
        create_data,
    ]
    METHOD_CHOICES = {
        'create': create_index,
        'delete': delete_index,
    }
    SPIDER_CHOICES = {
        'jobbole': None,
    }

    # help = 'which> 0:health, 1:ping, 2:create_index, 3:create_data, def:0'
    def methods(self):
        return " ".join(self.METHOD_CHOICES.keys())

    def spiders(self):
        return " ".join(self.SPIDER_CHOICES.keys())

    def add_arguments(self, parser):
        parser.add_argument('which', type=int, default=0)
        parser.add_argument('index', type=str, default='', help="which index want:" + " ".join(IndexDict.keys()))
        parser.add_argument('method', type=str, default='', help="methods:" + self.methods())
        # parser.add_argument('fakedata', type=int, default=0, help="Insert:" + " ".join(IndexDict.keys()))
        parser.add_argument('spider', type=str, default='', help="spider:" + self.spiders())

    def handle(self, **options):
        which = options.get('which', 0) % len(self.WHICH_CHOICES)
        if which in [0, 1, 2, 3]:
            func = self.WHICH_CHOICES[which]
            ret = func()
            self.stdout.write(ret)
        index = options.get('index', None)
        if not index and index in IndexDict:
            self.stdout.write('index is none')
            return
        method = options.get('method', None)
        method_func = self.METHOD_CHOICES.get(method, None)
        if method_func:
            ret = method_func(index)
            self.stdout.write(ret)
        # fakedata = options.get('fakedata', False)
        # if fakedata == 0 and index == 'Danmu':
        #     ret = 'fakedata'
        #     self.stdout.write(ret)
        spider = options.get('spider', False)
        if hasattr(spider, 'run'):
            ret = spider.run()
            self.stdout.write(ret)
