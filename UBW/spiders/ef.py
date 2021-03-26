import scrapy
from lxml import etree
import requests
from scrapy.http.response.html import HtmlResponse


class EfSpider(scrapy.Spider):
    name = 'center.ef.com.cn'.replace('.', '_')
    start_urls = ['http://center.ef.com.cn/']
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
        url = 'http://center.ef.com.cn/dict/'
        for word in word_list:
            yield response.follow(url=url + word + '/', callback=self.get_word)

    def get_word(self, response: HtmlResponse):
        if response.status == 302 or response.status == 404:
            return
        text = response.text
        html = etree.HTML(text)
        zh = [zh.xpath('string(.)') for zh in html.xpath("//span[@class='translate']")]
        en = [eg.xpath('string(.)') for eg in html.xpath("//span[@class='eg']")]
        for word in zip(zh, en):
            yield {'key': word[0], 'en': word[1]}
