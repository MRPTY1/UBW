import scrapy
from lxml import etree
import requests
from scrapy.http.response.html import HtmlResponse
import re


class MydictSpider(scrapy.Spider):
    name = 'www.mydict.uk'.replace('.', '_')
    start_urls = ['https://www.mydict.uk']
    custom_settings = {
        'LOG_LEVEL': 'DEBUG',
        'REDIRECT_ENABLED': False,
        'DOWNLOAD_DELAY': 3,
        'DOWNLOADER_MIDDLEWARES': {
            'UBW.middlewares.ProxiesMiddleware': 543
        },
        'CONCURRENT_REQUESTS': 1,
        'ITEM_PIPELINES': {
            'UBW.pipelines.KVPipeline': 300,
        },
        'COOKIES_ENABLED': False,
    }

    def parse(self, response: HtmlResponse, **kwargs):
        text = requests.get('http://192.168.99.18/en_50k.lang').text
        word_list = text.split('\n')
        for word in word_list:
            url1 = f'https://www.mydict.uk/Dictionary/English-Chinese/{word}'
            url2 = f'https://www.mydict.uk/Dictionary/English-German/{word}'
            yield response.follow(url=url1, callback=self.get_word)
            yield response.follow(url=url2, callback=self.get_word)

    def get_word(self, response: HtmlResponse):
        text = response.text
        html = etree.HTML(text)
        key_list = [re.sub(r'[\r\n\t]| {2,}', '', key.xpath('string(.)')) for key in
                    html.xpath('//div[@class="wiki"]/div[4]//li/div[2]')]
        val_list = [re.sub(r'[\r\n\t]| {2,}', '', key.xpath('string(.)')) for key in
                    html.xpath('//div[@class="wiki"]/div[4]//li/div[1]')]
        for kv in zip(key_list, val_list):
            yield {'key': kv[0], 'val': kv[1]}
