import scrapy
from lxml import etree
import requests
from scrapy.http.response.html import HtmlResponse
import re


class GetSpider(scrapy.Spider):
    name = 'lawyer.get.com.tw'.replace('.', '_')
    start_urls = ['http://lawyer.get.com.tw/']

    custom_settings = {
        'LOG_LEVEL': 'DEBUG',
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
            url = f'http://lawyer.get.com.tw/Dic/Default.aspx?iPageNo=1&sFilter={word}'
            yield response.follow(url=url, callback=self.get_list, meta={'word': word})

    def get_list(self, response: HtmlResponse):
        text = response.text
        re_page = re.search(r'第 \d+ 頁,共 (\d+) 頁', text)
        if re_page:
            for page in range(1, int(re_page.group(1)) + 1):
                url = f'http://lawyer.get.com.tw/Dic/Default.aspx?iPageNo={page}&sFilter={response.meta["word"]}'
                yield response.follow(url=url, callback=self.get_word)

    def get_word(self, response: HtmlResponse):
        text = response.text
        html = etree.HTML(text)
        key_list = [key.xpath('string(.)') for key in html.xpath('//td[@class="dic"]//tr/td[2]/a')]
        val_list = [val.xpath('string(.)') for val in html.xpath('//td[@class="dic"]//tr/td[1]/a')]
        for kv in zip(key_list, val_list):
            if len(kv[0]) and len(kv[1]):
                yield {'key': kv[0], 'val': kv[1]}
