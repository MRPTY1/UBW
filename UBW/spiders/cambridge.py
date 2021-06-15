import scrapy
from lxml import etree
import requests
from scrapy.http.response.html import HtmlResponse


class CambridgeSpider(scrapy.Spider):
    name = 'dictionary.cambridge.org'.replace('.', '_')
    start_urls = ['https://dictionary.cambridge.org/']
    custom_settings = {
        'LOG_LEVEL': 'INFO',
        'DOWNLOADER_MIDDLEWARES': {
            'UBW.middlewares.VPNMiddleware': 543
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
            url1 = f'https://dictionary.cambridge.org/dictionary/english-chinese-simplified/{word}'
            url2 = f'https://dictionary.cambridge.org/dictionary/english-chinese-traditional/{word}'
            yield response.follow(url=url1, callback=self.get_word)
            yield response.follow(url=url2, callback=self.get_word)

    def get_word(self, response: HtmlResponse):
        text = response.text
        html = etree.HTML(text)
        key_list = [key.xpath('string(.)') for key in
                    html.xpath('//div[@class="def-body ddef_b"]/div[@class="examp dexamp"]/span[@class="eg deg"]')]
        if 'chinese-traditional' in response.url:
            pass
            val_list = [val.xpath('string(.)') for val in
                        html.xpath('//div[@class="def-body ddef_b"]/div[@class="examp dexamp"]/span[@lang="zh-Hant"]')]
        else:
            val_list = [val.xpath('string(.)') for val in
                        html.xpath('//div[@class="def-body ddef_b"]/div[@class="examp dexamp"]/span[@lang="zh-Hans"]')]
        for kv in zip(key_list, val_list):
            if len(kv[0]) and len(kv[1]):
                yield {'key': kv[0], 'val': kv[1], 'url': response.url}
