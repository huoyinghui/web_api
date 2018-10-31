from datetime import datetime, timezone
from elasticsearch_dsl import Document, Date, Integer, Keyword, Text, connections, Completion, DocType

# Define a default Elasticsearch client
client = connections.create_connection(hosts=['localhost'])


class Article(Document):
    title = Text(analyzer='ik_smart', fields={'raw': Keyword()})
    body = Text(analyzer='ik_smart')
    tags = Keyword()
    published_from = Date(default_timezone=timezone.utc)
    lines = Integer()

    class Index:
        name = 'blog'
        # settings = {
        #   "number_of_shards": 2,
        # }

    def save(self, ** kwargs):
        self.lines = len(self.body.split())
        return super(Article, self).save(** kwargs)

    def is_published(self):
        return datetime.now() > self.published_from


class BlogLive(Document):
    subject = Text(analyzer='ik_smart', fields={'raw': Keyword()})
    description = Text(analyzer='ik_smart', fields={'raw': Keyword()})
    topics = Keyword()
    live_suggest = Completion()
    published_from = Date()

    class Index:
        name = 'bloglive'

    def save(self, ** kwargs):
        return super(BlogLive, self).save(** kwargs)

    def is_published(self):
        return datetime.now() > self.published_from


class Danmu(Document):
    content = Text(analyzer='ik_smart', fields={'raw': Keyword()})
    opername = Keyword()
    tags = Keyword()
    published_from = Date()

    class Index:
        name = 'danmu'

    def save(self, ** kwargs):
        return super(Article, self).save(** kwargs)

    def is_published(self):
        return datetime.now() > self.published_from

