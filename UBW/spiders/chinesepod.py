import scrapy
import re
from lxml import etree
import requests
from scrapy.http.response.html import HtmlResponse


class ChinesepodSpider(scrapy.Spider):
    name = 'chinesepod.com'.replace('.', '_')
    start_urls = ['https://chinesepod.com/']
    custom_settings = {
        'DOWNLOAD_DELAY': 3,
        'LOG_LEVEL': 'DEBUG',
        'CONCURRENT_REQUESTS': 1,
        'ITEM_PIPELINES': {
            'UBW.pipelines.KVPipeline': 300,
        },
        'COOKIES_ENABLED': False,
    }

    def parse(self, response: HtmlResponse, **kwargs):
        text = requests.get('http://192.168.99.18/en_50k.lang').text
        word_list = text.split('\n')
        url = 'https://chinesepod.com/dictionary/english-chinese/'
        for word in word_list:
            yield response.follow(url=url + word, callback=self.get_word)

    def get_word(self, response: HtmlResponse):
        text = response.text
        text = re.sub(r'(<span.+?>|</span>|<br/>)', '', text)
        text = re.sub(r'<div class="dict-pinyin-cont">[\w\W]+?</div>', '</td><td>', text)
        html = etree.HTML(text)
        zh_list = [zh for zh in html.xpath('//tr/td[1]/text()')]
        en_list = [en for en in html.xpath('//tr/td[2]/text()')]
        for word in zip(zh_list, en_list):
            yield {'key': re.sub(r'([\r\n\t]| {2,})', '', word[0]), 'en': re.sub(r'([\r\n\t]| {2,})', '', word[1])}
