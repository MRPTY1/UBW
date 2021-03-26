import scrapy
from lxml import etree
import requests
from scrapy.http.response.html import HtmlResponse


class FengzxSpider(scrapy.Spider):
    name = 'dict.fengzx.com'.replace('.', '_')
    start_urls = ['http://dict.fengzx.com/']
    custom_settings = {
        'LOG_LEVEL': 'INFO',
        'CONCURRENT_REQUESTS': 32,
        'ITEM_PIPELINES': {
            'UBW.pipelines.KVPipeline': 300,
        },
        'DOWNLOADER_MIDDLEWARES': {
            'UBW.middlewares.ProxiesMiddleware': 543
        },
        'COOKIES_ENABLED': False,
    }

    def parse(self, response: HtmlResponse, **kwargs):
        text = requests.get('http://192.168.99.18/en_50k.lang').text
        word_list = text.split('\n')
        url = 'http://dict.fengzx.com/s.php?keyword='
        for word in word_list:
            yield response.follow(url=url + word, callback=self.get_word)

    def get_word(self, response: HtmlResponse):
        text = response.text
        html = etree.HTML(text)
        zh = [zh for zh in html.xpath('//li[@style="margin-bottom:15px;"]/text()')]
        en = [eg.xpath('string(.)') for eg in html.xpath('//li[@style="margin-bottom:15px;"]/span')]
        for word in zip(zh, en):
            yield {'key': word[0], 'en': word[1]}
