import scrapy
from lxml import etree
import requests
from scrapy.http.response.html import HtmlResponse
import re


class BigearSpider(scrapy.Spider):
    name = 'dict.bigear.cn'.replace('.', '_')
    start_urls = ['http://dict.bigear.cn/']
    custom_settings = {
        'LOG_LEVEL': 'INFO',
        'DOWNLOADER_MIDDLEWARES': {
            'UBW.middlewares.RandomProxiesMiddleware': 543
        },
        'CONCURRENT_REQUESTS': 16,
        'ITEM_PIPELINES': {
            'UBW.pipelines.KVPipeline': 300,
        },
        'COOKIES_ENABLED': False,
    }

    def parse(self, response: HtmlResponse, **kwargs):
        text = requests.get('http://192.168.99.18/en_50k.lang').text
        word_list = text.split('\n')
        for word in word_list:
            url = f'http://dict.bigear.cn/w/{word}/'
            yield response.follow(url=url, callback=self.get_word)

    def get_word(self, response: HtmlResponse):
        text = response.text
        html = etree.HTML(text)
        key_list = [key for key in html.xpath("//div[@id='sentence']/ul/li/div[@class='liright fr']/text()")]
        val_list = [val.xpath('string(.)') for val in
                    html.xpath("//div[@id='sentence']/ul/li/div[@class='liright fr']/span")]
        for kv in zip(key_list, val_list):
            yield {'key': kv[0], 'val': kv[1]}
