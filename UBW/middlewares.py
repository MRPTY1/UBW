import logging
import random
import time
from scrapy.http import HtmlResponse
from scrapy.downloadermiddlewares.retry import RetryMiddleware
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import scrapy


class VPNMiddleware:

    def process_request(self, request, spider):
        request.meta['proxy'] = 'https://192.168.99.13:7890'


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


class SeleniumMiddleware:
    def __init__(self):
        self.chrome_options = Options()
        self.chrome_options.add_argument("--headless")
        self.chrome = webdriver.Chrome(chrome_options=self.chrome_options)

    def process_request(self, request, spider):
        self.chrome.set_page_load_timeout(5)
        try:
            self.chrome.get(request.url)
        except Exception:
            self.chrome.execute_script('window.stop()')
        # self.chrome.get(request.url)
        body = self.chrome.page_source
        response = HtmlResponse(url=request.url, body=body.encode('utf-8'), encoding='utf-8', request=request)
        return response

    def __del__(self):
        self.chrome.quit()


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
