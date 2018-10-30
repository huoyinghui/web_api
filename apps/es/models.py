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


def create_data():
    # for i in range(10):
    init_test_data_random()
    return 'create data ok random'


def create_data_random():
    # for i in range(10):
    init_test_data_random()
    return 'create data ok'


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


def init_test_data_random():
    for id in range(1000, 10):
        id = id % 100 + id % 5 + 100
        add_article(id, 'Python is good!', 'Python is good!', ['python'])
        id = id % 101 + id % 5 + 200
        add_article(id, 'Elasticsearch', 'Distributed, open source search and analytics engine', ['elasticsearch'])
        id = id % 102 + id % 5 + 300
        add_article(id, 'Python very quickly', 'Python very quickly', ['python'])
        id = id % 103 + id % 5 + 400
        add_article(id, 'Django', 'Python Web framework', ['python', 'django'])
