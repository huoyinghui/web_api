from datetime import datetime
from elasticsearch_dsl import Document, Date, Integer, Keyword, Text, connections

# Define a default Elasticsearch client
client = connections.create_connection(hosts=['localhost'])


class Article(Document):
    title = Text(analyzer='snowball', fields={'raw': Keyword()})
    body = Text(analyzer='snowball')
    tags = Keyword()
    published_from = Date()
    lines = Integer()

    class Index:
        name = 'blog'
        settings = {
          "number_of_shards": 2,
        }

    def save(self, ** kwargs):
        self.lines = len(self.body.split())
        return super(Article, self).save(** kwargs)

    def is_published(self):
        return datetime.now() > self.published_from


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