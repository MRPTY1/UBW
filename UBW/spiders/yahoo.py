import scrapy
from scrapy.http.response.html import HtmlResponse
from lxml import etree
import re
import requests


class YahooSpider(scrapy.Spider):
    name = 'dictionary.search.yahoo.com'.replace('.', '_')
    start_urls = ['https://yahoo.com/']
    custom_settings = {
        'CONCURRENT_REQUESTS': 4,
        'DOWNLOADER_MIDDLEWARES': {
            'UBW.middlewares.VPNMiddleware': 543,
            'UBW.middlewares.PauseMiddleware': 600,
        },
        'ITEM_PIPELINES': {
            'UBW.pipelines.KVPipeline': 300,
        },
        'COOKIES_ENABLED': False,
        'DOWNLOAD_DELAY': 1,
        'SCHEDULER': "scrapy_redis.scheduler.Scheduler",
        'DUPEFILTER_CLASS': "scrapy_redis.dupefilter.RFPDupeFilter",
        'SCHEDULER_PERSIST': True,
        'SCHEDULER_QUEUE_CLASS': 'scrapy_redis.queue.PriorityQueue',
    }

    def parse(self, response: HtmlResponse, **kwargs):
        res = requests.get('http://159.75.19.163/FrequencyWords/en/en_50k.txt')
        text = re.sub(r' \d+', '', str(res.text.encode('iso8859'), encoding='utf-8'))
        word_list = text.split('\n')
        for word in word_list:
            url = f'https://hk.dictionary.search.yahoo.com/search?p={word}&ei=UTF-8&nojs=1'
            yield response.follow(url=url, callback=self.get_word)
            url = f'https://tw.dictionary.search.yahoo.com/search?p={word}&ei=UTF-8&nojs=1'
            yield response.follow(url=url, callback=self.get_word)

    def get_word(self, response: HtmlResponse):
        text = response.text
        html = etree.HTML(text)
        word_list = [word.xpath('string(.)') for word in html.xpath('//span[contains(@class,"fc-2nd")]')]
        for word in word_list:
            re_index = re.search(r'[\u4e00-\u9fa5]', word)
            if re_index:
                index = re_index.start()
                if index and re.search('[A-Za-z]', word):
                    yield {'key': word[0:index], 'val': word[index:], 'url': response.url}
