import scrapy
from scrapy.http.response.html import HtmlResponse
from lxml import etree
import re
import requests


class JapaneselawtranslationSpider(scrapy.Spider):
    name = 'www.japaneselawtranslation.go.jp.old'.replace('.', '_')
    start_urls = ['http://www.japaneselawtranslation.go.jp/']
    custom_settings = {
        'CONCURRENT_REQUESTS': 4,
        'DOWNLOADER_MIDDLEWARES': {
        },
        'ITEM_PIPELINES': {
            'UBW.pipelines.KVPipeline': 300,
        },
        'COOKIES_ENABLED': False,
    }

    def parse(self, response: HtmlResponse, **kwargs):
        text = requests.get('http://192.168.99.18/en_50k.lang').text
        word_list = text.split('\n')
        for word in word_list:
            url = f'http://www.japaneselawtranslation.go.jp/dict/list?re=01&ft=1&dn=1&ky={word}&x=0&y=0&co=1'
            yield response.follow(url=url, callback=self.get_list, meta={'word': word})

    def get_list(self, response: HtmlResponse):
        text = response.text
        re_page = re.search(r'(\d+)件中　1～20件を表示', text)
        if re_page:
            page_sum = int(re_page.group(1)) // 200
            for page in range(1, page_sum + 1):
                url = f'http://www.japaneselawtranslation.go.jp/Dict/viewList/?' \
                      f'dn=4&x=0&y=0&re=01&ft=1&ky={response.meta["word"]}&co=1&page={page}'
                yield response.follow(url=url, callback=self.get_word, priority=10)

    def get_word(self, response: HtmlResponse):
        text = response.text
        html = etree.HTML(text)
        word_list = [word for word in html.xpath('//td[text()="【用例】"]/../td[2]/text()')]
        key_list = [re.sub(r'[\r\n]', '', word_list[i]) for i in range(0, len(word_list)) if i % 2 == 0]
        val_list = [re.sub(r'[\r\n]', '', word_list[i]) for i in range(0, len(word_list)) if i % 2 != 0]
        for kv in zip(key_list, val_list):
            yield {'key': kv[0], 'val': kv[1]}
