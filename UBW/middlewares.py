import logging
import random
import time
import scrapy
import requests
from scrapy.core.downloader.handlers.http11 import TunnelError
from scrapy.http.response.html import HtmlResponse
import re
from scrapy.downloadermiddlewares.retry import RetryMiddleware


class V2rayNMiddleware:

    def process_request(self, request, spider):
        request.meta['proxy'] = 'https://127.0.0.1:10809'


class ProxiesMiddleware:

    def process_request(self, request, spider):
        if 'https' in request.url:
            request.meta['proxy'] = 'https://159.75.19.163:10086'
        else:
            request.meta['proxy'] = 'http://159.75.19.163:10086'


class RandomProxiesMiddleware:

    def process_request(self, request, spider):
        if random.getrandbits(1):
            if 'https' in request.url:
                request.meta['proxy'] = 'https://159.75.19.163:10086'
            else:
                request.meta['proxy'] = 'http://159.75.19.163:10086'


class SeleniumInterceptMiddleware:

    def process_request(self, request, spider):
        spider.chrome.get(request.url)
        return scrapy.http.HtmlResponse(url=spider.chrome.current_url, body=spider.chrome.page_source,
                                        encoding='utf-8', request=request, status=200)


class PauseMiddleware(RetryMiddleware):
    def __init__(self, crawler):
        self.logger = logging.getLogger("PauseMiddleware")
        super(PauseMiddleware, self).__init__(crawler.settings)
        self.crawler = crawler

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    def process_response(self, request, response, spider):
        if response.status in [500, 429]:
            self.crawler.engine.pause()
            self.logger.debug('引擎暂停')
            time.sleep(300)
            self.logger.debug('引擎重启')
            self.crawler.engine.unpause()
            return request
        else:
            return response


class ProxiesPoolMiddleware:

    def process_request(self, request, spider):
        res = requests.get('http://192.168.99.18:5010/get_status')
        if res.json().get('count') and '192.168.99.18' not in request.url:
            proxy = requests.get('http://192.168.99.18:5010/get').json().get('proxy')
            request.meta['proxy'] = 'https://' + proxy
        else:
            print('代理池为空')

    def process_response(self, request, response: HtmlResponse, spider):
        if response.status in [429, 403, 400, 405] and '192.168.99.18' not in request.url:
            requests.get(f'http://192.168.99.18:5010/delete?proxy={request.meta["proxy"]}')
            return request
        else:
            return response

    def process_exception(self, request, exception, spider):
        if isinstance(exception, TunnelError):
            requests.get(f'http://192.168.99.18:5010/delete?proxy={re.sub(r"http.*/", "", request.meta["proxy"])}')
            return request
