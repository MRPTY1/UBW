import scrapy
from scrapy.http.response.html import HtmlResponse
from urllib import parse
from lxml import etree
import re


class ElrcShareSpider(scrapy.Spider):
    name = 'elrc-share.eu'.replace('.', '_')
    start_urls = ['http://elrc-share.eu/']
    custom_settings = {
        'CONCURRENT_REQUESTS': 8,
        'ITEM_PIPELINES': {
            'UBW.pipelines.MongoPipeline': 300,
        },
        'COOKIES_ENABLED': False
    }

    def parse(self, response: HtmlResponse, **kwargs):
        url = 'https://elrc-share.eu/repository/search/'
        params = {
            'q': 'Parallel Corpus',
            'selected_facets': 'multilingualityTypeFilter_exact:Parallel',
            'page': 1
        }
        key_words = ['parallel corpora', 'bilingual', 'corpus', 'Parallel', 'Corpus', 'Corp', 'translte']
        for key_word in key_words:
            params['q'] = key_word
            yield response.follow(url=url + '?' + parse.urlencode(params), callback=self.get_url, meta=params)

    def get_url(self, response: HtmlResponse):
        url = 'https://elrc-share.eu/repository/search/'
        params = response.meta
        href_list = re.findall(r'\w{64}/', response.text)
        if len(href_list) == 0:
            return None
        else:
            params['page'] += 1
            print(url + '?' + parse.urlencode(params))
            yield response.follow(url=url + '?' + parse.urlencode(params), callback=self.get_url, meta=params)
            for href in href_list:
                yield {'url': 'https://elrc-share.eu/repository/download/' + href}
