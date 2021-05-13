import scrapy
from scrapy.http.response.html import HtmlResponse
from lxml import etree
import re
import requests


class LexicoSpider(scrapy.Spider):
    name = 'www.lexico.com'.replace('.', '_')
    start_urls = ['https://www.lexico.com/']
    custom_settings = {
        # 'CONCURRENT_REQUESTS': 2,
        'DOWNLOADER_MIDDLEWARES': {
            # 'UBW.middlewares.V2rayNMiddleware': 543,
            # 'UBW.middlewares.PauseMiddleware': 600,
            'UBW.middlewares.SeleniumMiddleware': 544,
        },
        'ITEM_PIPELINES': {
            'UBW.pipelines.KVPipeline': 300,
        },
        # 'COOKIES_ENABLED': False,
        # 'DOWNLOAD_DELAY': 1,
        # 'SCHEDULER': "scrapy_redis.scheduler.Scheduler",
        # 'DUPEFILTER_CLASS': "scrapy_redis.dupefilter.RFPDupeFilter",
        # 'SCHEDULER_PERSIST': True,
        # 'SCHEDULER_QUEUE_CLASS': 'scrapy_redis.queue.PriorityQueue',
    }

    def parse(self, response: HtmlResponse, **kwargs):
        print(response.text)
        text = requests.get('http://159.75.19.163/FrequencyWords/en/en_50k.txt').text
        text = re.sub(r' \d+', '', text)
        word_list = text.split('\n')
        for word in word_list:
            url = f'https://www.lexico.com/en-es/translate/{word}?s=t'
            yield response.follow(url=url, callback=self.get_word)

    def get_word(self, response: HtmlResponse, **kwargs):
        text = response.text
        print(text)
        html = etree.HTML(text)
        for div in html.xpath('//div[@class="ex"]'):
            word_list = [em for em in div.xpath('em/text()')]
            if len(word_list) == 2:
                yield {'url': response.url, 'key': word_list[0], 'val': word_list[1]}
