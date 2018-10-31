# -*- coding:utf-8 -*-
import os
import threading
import logging
import aiohttp
import asyncio
import async_timeout
import time
from random import random
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from lxml import etree
from pyquery import PyQuery as pq

from es.index import add_article
from es.models import Article


logging.basicConfig(
    filename='async_log.txt',
    level=logging.INFO,
    format='%(asctime)s:%(funcName)15s:%(lineno)5s%(levelname)8s:%(name)10s:%(message)s',
    datefmt='%Y/%m/%d %I:%M:%S'
)
logger = logging.getLogger('spider')

ua = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'


class MulTaskManage(object):

    def __init__(self, count=0):
        self.count = count

    @staticmethod
    def mul_task_pool(max_workers=3, mod=0, task_dict=None):
        """
        多任务
        :param max_workers:
        :param mod:
        :param task_dict:
        :return:

        with ProcessPoolExecutor(max_workers=2) as executor:
            task1 = executor.submit(task)
            task2 = executor.submit(task)

        with ThreadPoolExecutor(max_workers=3) as executor:
            task1 = executor.submit(task_io)
            task2 = executor.submit(task_io)
        """
        if not isinstance(task_dict, dict):
            return
        mul_mod = ProcessPoolExecutor if mod == 0 else ThreadPoolExecutor
        future_to_data = {}
        with mul_mod(max_workers=max_workers) as executor:
            # future_to_data = [executor.submit(task) for task in task_list]
            for task_key, task_func in task_dict.items():
                fn, arg, kwarg = task_func
                print(task_key, fn, arg, kwarg)
                future_task = executor.submit(fn, *arg, **kwarg)
                future_to_data[task_key] = future_task
                print("future dict:", future_to_data)

        return future_to_data


class Spider(object):
    def __init__(self, count=0, queue=None, user_agent='', urls=None):
        """

        :param count:
        :param queue:
        :param user_agent:
        :param urls:
        """
        self.count = count
        self.queue = queue
        self.user_agent = user_agent
        self.urls = urls
        self.url_prefix = 'http://python.jobbole.com/'

    @staticmethod
    def new_id(id_=''):
        if not id_:
            return None
        return 'jobble_{}'.format(id_)

    def url_to_id(self, url=''):
        id_ = str(url)[len(self.url_prefix):].replace('/', '', -1)
        return id_

    async def fetch(self, session, url):
        head = {'User-Agent': self.user_agent}
        with async_timeout.timeout(10):
            async with session.get(url, headers=head) as response:
                html_text = await response.text()
                # file = pyquery(html_text)
                html = etree.HTML(html_text)
                title_list = html.xpath('//*[@id="archive"]//a[@class="archive-title"]/text()')
                href_list = html.xpath('//*[@id="archive"]//span[@class="read-more"]/a/@href')
                return dict(zip(title_list, href_list))
                # return file('.archive-title').eq(0).text()

    async def fetch_detail(self, session, url):
        head = {'User-Agent': self.user_agent}
        with async_timeout.timeout(60):
            async with session.get(url, headers=head) as response:
                await asyncio.sleep(0.1)
                html_text = await response.text()
                file = pq(html_text)
                return file('.entry').text()

    async def bulk_article(self, queue=None):
            while True:
                item = await queue.get()
                self.count += 1
                logger.info('cnt:{} consuming item {}...'.format(self.count, item))
                if item is None:
                    logging.debug('consume finish')
                    break
                await asyncio.sleep(random())
                print(item)
                if not isinstance(item, Article):
                    continue
                # bulk
                item.save()
                # add_article(id_=self.new_id(id_), title=title, body=describe, tags=[])

    async def consume(self, queue=None):
        async with aiohttp.ClientSession() as session:
            while True:
                item = await queue.get()
                self.count += 1
                logger.info('cnt:{} consuming item {}...'.format(self.count, item))
                if item is None:
                    logging.debug('consume finish')
                    break
                await asyncio.sleep(random())
                id_, describe_url, title = item
                describe = await self.fetch_detail(session, describe_url)
                add_article(title=title, body=describe, tags=[])
                # add_article(id_=self.new_id(id_), title=title, body=describe, tags=[])

    async def produce(self, queue=None):
        async with aiohttp.ClientSession() as session:
            for url in self.urls:
                page_data = await self.fetch(session, url)
                for title, describe_url in page_data.items():
                    if not str(describe_url).startswith(self.url_prefix):
                        continue
                    id_ = self.url_to_id(describe_url)
                    item = (id_, describe_url, title)
                    await queue.put(item)
        logging.debug('produce end:', queue.qsize())
        await queue.put(None)


async def spider_jobble():
    urls = ['http://python.jobbole.com/category/news/page/{}/'.format(i) for i in range(1, 2)]
    spider = Spider(urls=urls, user_agent=ua)
    async with aiohttp.ClientSession() as session:
        for url in urls:
            page_data = await spider.fetch(session, url)
            for title, describe_url in page_data.items():
                if not str(describe_url).startswith(spider.url_prefix):
                    continue
                id_ = spider.url_to_id(describe_url)
                describe = await spider.fetch_detail(session, describe_url)
                add_article(id_=spider.new_id(id_), title=title, body=describe, tags=[])


def task_long_io(*args, **kwargs):
    time.sleep(3)
    return "Process:{} Thread:{} args:{} kwargs:{}".format(
        os.getpid(), threading.get_ident(), args, kwargs
    )


def main_async():
    loop = asyncio.get_event_loop()
    urls = ['http://python.jobbole.com/category/news/page/{}/'.format(i) for i in range(1, 2)]
    spider = Spider(urls=urls, user_agent=ua)
    queue = asyncio.Queue(maxsize=5, loop=loop)
    producer_coro = spider.produce(queue)
    consumer_coro = spider.consume(queue)
    bulk_article_coro = spider.bulk_article(queue)
    try:
        loop.run_until_complete(asyncio.gather(producer_coro, consumer_coro))
        # loop.run_until_complete(spider_jobble())
    except Exception as ext:
        print(ext)
        logger.error(ext)
    print('spider finish')


def main_sync():
    future_data_dict = MulTaskManage.mul_task_pool(
        max_workers=3,
        mod=0,
        task_dict=dict(
            zip(
                ["{}".format(i) for i in range(3)],
                [
                    (task_long_io, (1, 2, 3), dict(name='hello1')),
                    (task_long_io, (11, 22, 33), dict(name='hello2')),
                    (task_long_io, (111, 222, 333), dict(name='hello3')),
                ]
            )
        )
    )
    # 获取结果
    for task_key, task_future in future_data_dict.items():
        from concurrent.futures import Future
        if not isinstance(task_future, Future):
            continue
        print(task_key, task_future, task_future.result(timeout=None))


def main():
    # main_async()
    main_sync()


if __name__ == '__main__':
    main()
