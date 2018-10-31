# -*- coding:utf-8 -*-
import os
import logging
import aiohttp
import asyncio
import async_timeout
import time
import threading
from random import random
from threading import Lock as TLock
from multiprocessing import Lock as PLock
from multiprocessing import Manager
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, Future

from lxml import etree
from pyquery import PyQuery as pq

from es.index import add_article, bulk_insert
from es.models import Article


logging.basicConfig(
    filename='async_log.txt',
    level=logging.INFO,
    format='%(asctime)s:%(funcName)15s:%(lineno)5s%(levelname)8s:%(name)10s:%(message)s',
    datefmt='%Y/%m/%d %I:%M:%S'
)
logger = logging.getLogger('spider')

ua = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'
g = 0
g_td = {}


class MulTaskManage(object):
    """
    多任务类，执行多任务，屏蔽
    """

    @staticmethod
    def mul_task_pool(max_workers=3, mod=0, task_dict=None):
        """
        多任务
        :param max_workers:
        :param mod:
        :param task_dict:
        :return:

        """
        if not isinstance(task_dict, dict):
            return
        mul_mod = ProcessPoolExecutor if mod == 0 else ThreadPoolExecutor
        future_to_data = {}
        with mul_mod(max_workers=max_workers) as executor:
            # future_to_data = [executor.submit(task) for task in task_list]
            for task_key, task_func in task_dict.items():
                fn, arg, kwarg = task_func
                logging.debug("task_key:{} fn:{} arg:{} kwarg:{}".format(task_key, fn, arg, kwarg))
                future_task = executor.submit(fn, *arg, **kwarg)
                # 主进程/线程完成
                future_to_data[task_key] = future_task
                logging.debug("future dict:{}".format(future_to_data))
        return future_to_data


class Spider(object):
    def __init__(self, name='', count=0, queue=None, user_agent='', urls=None):
        """

        :param name:
        :param count:
        :param queue:
        :param user_agent:
        :param urls:
        """
        self.name = name if name else 'spider'
        self.count = count
        self.queue = queue
        self.user_agent = user_agent
        self.urls = urls
        self.url_prefix = 'http://python.jobbole.com/'
        self.data_queue_limit = 10
        self.xpath_title_list = '//*[@id="archive"]//a[@class="archive-title"]/text()'
        self.xpath_href_list = '//*[@id="archive"]//span[@class="read-more"]/a/@href'
        self.query_class_detail = '.entry'

    def new_id(self, id_=''):
        if not id_:
            return None
        return '{}_{}'.format(self.name, id_)

    def url_to_id(self, url=''):
        id_ = str(url)[len(self.url_prefix):].replace('/', '', -1)
        return id_

    async def fetch(self, session, url):
        head = {'User-Agent': self.user_agent}
        with async_timeout.timeout(10):
            async with session.get(url, headers=head) as response:
                html_text = await response.text()
                html = etree.HTML(html_text)
                title_list = html.xpath(self.xpath_title_list)
                href_list = html.xpath(self.xpath_href_list)
                return dict(zip(title_list, href_list))

    async def fetch_detail(self, session, url):
        head = {'User-Agent': self.user_agent}
        with async_timeout.timeout(60):
            async with session.get(url, headers=head) as response:
                await asyncio.sleep(0.1)
                html_text = await response.text()
                file = pq(html_text)
                return file(self.query_class_detail).text()

    async def bulk_article(self, data_queue=None):
            item_list = []
            while True:
                item = await data_queue.get()
                self.count += 1
                logger.info('cnt:{} consuming item {}...bulk:{}'.format(self.count, item, len(item_list)))
                if item is None:
                    logging.info('consume finish:{}'.format(data_queue.qsize()))
                    break
                await asyncio.sleep(random())
                if not isinstance(item, Article):
                    continue
                # bulk insert
                item_list.append(item.to_dict(True))
                if len(item_list) >= self.data_queue_limit:
                    bulk_insert(tuple(item_list))
                    item_list = []

    async def consume(self, queue=None, data_queue=None):
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
                data = add_article(title=title, body=describe, tags=[])
                await data_queue.put(data)
                # add_article(id_=self.new_id(id_), title=title, body=describe, tags=[])
            await data_queue.put(None)

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
        logging.info('produce end:', queue.qsize())
        await queue.put(None)


async def spider_job():
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
    """
    被多个进程/或者线程并发执行

    :param args:
    :param kwargs:
    :return:
    """

    global g
    mod_lock = args[0]
    if not mod_lock:
        return
    # g 在各个线程均可见，且共享，需要加线程锁保护
    # g 在各个进程均独立, 修改互不影响
    mod = kwargs.get('mod', 1)
    print('pid:{} tid:{} mod:{} wait lock:{}'.format(os.getpid(), threading.get_ident, mod, mod_lock))
    if mod:
        # 多线程，全局变量共享，加锁修改
        with mod_lock:
            g_td[kwargs['name']+'_bf'] = g
            print("bf pid:{} g:{} id_g:{} id_mod_lock:{} kwargs:{} td:{}".format(
                os.getpid(), g, id(g), id(mod_lock), kwargs, g_td)
            )
            g = g + 1
            time.sleep(0.05)
            g_td[kwargs['name']+'_af'] = g
            print("af pid:{} g:{} id_g:{} id_mod_lock:{} kwargs:{} td:{}".format(
                os.getpid(), g, id(g), id(mod_lock), kwargs, g_td)
            )
    else:
        # 多进程并行, 地址空间相互独立, 无需锁
        # 若需要串行，则加锁, 加锁后的代码变为多进程串行
        with mod_lock:
            td = args[1]
            td[kwargs['name']+'_bf'] = g
            print("bf pid:{} g:{} id_g:{} id_mod_lock:{} kwargs:{} td:{}".format(
                os.getpid(), g, id(g), id(mod_lock), kwargs, td)
            )
            g = g + 1
            time.sleep(2)
            td[kwargs['name']+'_af'] = g
            print("af pid:{} g:{} id_g:{} id_mod_lock:{} kwargs:{} td:{}".format(
                os.getpid(), g, id(g), id(mod_lock), kwargs, td)
            )
    print('pid:{} tid:{} task end'.format(os.getpid(), threading.get_ident()))
    return "Process:{} Thread:{} args:{} kwargs:{}".format(
        os.getpid(), threading.get_ident(), args, kwargs
    )


def main_async():
    loop = asyncio.get_event_loop()
    urls = ['http://python.jobbole.com/category/news/page/{}/'.format(i) for i in range(1, 2)]
    spider = Spider(urls=urls, user_agent=ua)
    queue = asyncio.Queue(maxsize=5, loop=loop)
    producer_coro = spider.produce(queue)
    data_queue = asyncio.Queue(maxsize=5, loop=loop)
    consumer_coro = spider.consume(queue, data_queue)
    bulk_article_coro = spider.bulk_article(data_queue)
    try:
        loop.run_until_complete(
            asyncio.gather(
                producer_coro,
                consumer_coro,
                bulk_article_coro
            )
        )
        # 单独测试
        # loop.run_until_complete(spider_job())
    except Exception as ext:
        print(ext)
        logger.error(ext)
    logging.info('spider finish')


def main_sync():
    task_dict = {}
    # n = 2, 4, 6, 8, 10
    # worker = 2
    # 执行次数=n/worker, 每一批的worker在
    mul_task_num = 2
    mod = 0
    t_lock = TLock()
    p_lock = PLock()
    p_m_lock = Manager().Lock()
    td = Manager().dict()
    print(id(t_lock), id(p_lock), id(p_m_lock), id(td), os.getpid())
    for i in range(mul_task_num):
        task_key = 'task_{}'.format(i)
        fn = task_long_io
        lock = t_lock if mod else p_m_lock
        args = (lock, td)
        kwargs = dict(name="name_{}".format(i), mod=mod)
        task_dict[task_key] = (fn, args, kwargs)

    future_data_dict = MulTaskManage.mul_task_pool(
        max_workers=2,
        mod=mod,
        task_dict=task_dict
    )
    # 获取结果
    for task_key, task_future in future_data_dict.items():
        if not isinstance(task_future, Future):
            continue
        logging.info("task_key:{} future:{} task_fn_return:{}".format(
            task_key, task_future, task_future.result(timeout=None))
        )


def main():
    # main_async()
    main_sync()


if __name__ == '__main__':
    main()
