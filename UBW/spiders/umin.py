import scrapy
from lxml import etree
import requests
from scrapy.http.response.html import HtmlResponse
import re


class UminSpider(scrapy.Spider):
    name = 'plaza.umin.ac.jp'.replace('.', '_')
    start_urls = ['http://plaza.umin.ac.jp/']
    custom_settings = {
        'LOG_LEVEL': 'DEBUG',
        'CONCURRENT_REQUESTS': 8,
        'ITEM_PIPELINES': {
            'UBW.pipelines.KVPipeline': 300,
        },
        'COOKIES_ENABLED': False,
    }

    def parse(self, response: HtmlResponse, **kwargs):
        for i in range(65, 123):
            url = f'http://plaza.umin.ac.jp/JPS1927/glossary/ex-glossary-{chr(i)}.htm'
            yield response.follow(url=url, callback=self.get_word)

    def get_word(self, response: HtmlResponse):
        text = response.text
        html = etree.HTML(text)
        key_list = [key for key in html.xpath('//*[@id="content"]/table[2]//tr/td[2]/font/text()')]
        val_list = [val for val in html.xpath('//*[@id="content"]/table[2]//tr/td[3]/font/text()')]
        for kv in zip(key_list, val_list):
            yield {'key': kv[0], 'val': kv[1]}
