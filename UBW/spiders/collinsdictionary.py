import scrapy
import re
from lxml import etree
import requests
from scrapy.http.response.html import HtmlResponse


class CollinsdictionarySpider(scrapy.Spider):
    name = 'www.collinsdictionary.com'.replace('.', '_')
    start_urls = ['https://www.collinsdictionary.com/']
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
        url = 'https://www.collinsdictionary.com/dictionary/english-chinese/'
        for word in word_list:
            yield response.follow(url=url + word, callback=self.get_word)

    def get_word(self, response: HtmlResponse):
        text = response.text
        html = etree.HTML(text)
        en_list, zh_list = [], []
        for q in html.xpath("//span[@class='orth']/q/text()"):
            en_list.append(q.replace(' ⇒ ', ''))
        for q in html.xpath('//div[@class="p phrase"]/span[@class="phr"]/span/text()'):
            en_list.append(q)
        zh_list = [zh for zh in html.xpath('//div[@class="cit cit-type-example"]/span[2]//q/text()')]
        for q in html.xpath('//div[@class="p phrase"]/span[@class="cit cit-type-translation"]//q/text()'):
            zh_list.append(re.sub(r'\(.*?\)', '', q))
        for word in zip(zh_list, en_list):
            yield {'key': word[0], 'en': word[1]}
