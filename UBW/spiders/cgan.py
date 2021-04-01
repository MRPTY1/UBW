import scrapy
from lxml import etree
import requests
import re
from scrapy.http.response.html import HtmlResponse


class CganSpider(scrapy.Spider):
    name = 'www.cgan.net'.replace('.', '_')
    start_urls = ['http://www.cgan.net/']
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
            url = f'http://www.cgan.net/cidian/?s={word}'
            yield response.follow(url=url, callback=self.get_list, meta={'word': word})

    def get_list(self, response: HtmlResponse):
        text = response.text
        re_page = re.search(r'第 1 页，共 (\d+) 页', text)
        if re_page:
            for i in range(1, int(re_page.group(1)) + 1):
                url = f'http://www.cgan.net/cidian/?s={response.meta["word"]}&paged={i}'
                yield response.follow(url=url, callback=self.get_word)

    def get_word(self, response: HtmlResponse):
        text = response.text
        html = etree.HTML(text)
        key_list = [key for key in html.xpath('//div/a[@rel="bookmark"]/p/text()')]
        val_list = [val for val in html.xpath('//div/a[@rel="bookmark"]/@title')]
        for kv in zip(key_list, val_list):
            yield {'key': kv[0], 'val': kv[1], 'url': response.url}
        key_list = [key for key in html.xpath('//div[@class="cnexplain"]/text()')]
        val_list = [val for val in html.xpath('//div[@class="cnword"]/text()')]
        for kv in zip(key_list, val_list):
            yield {'key': kv[0], 'val': kv[1], 'url': response.url}
