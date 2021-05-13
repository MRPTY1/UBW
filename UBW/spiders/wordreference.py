import scrapy
from scrapy.http.response.html import HtmlResponse
from lxml import etree
import re
import requests


class WordreferenceSpider(scrapy.Spider):
    name = 'www.wordreference.com'.replace('.', '_')
    start_urls = ['https://www.wordreference.com/']
    custom_settings = {
        'CONCURRENT_REQUESTS': 1,
        'DOWNLOADER_MIDDLEWARES': {
            # 'UBW.middlewares.SeleniumMiddleware': 544,
        },
        'ITEM_PIPELINES': {
            'UBW.pipelines.MongoPipeline': 300,
        },
        'COOKIES_ENABLED': False,
    }

    def parse(self, response: HtmlResponse, **kwargs):
        print(response.text)
        es_res = requests.get('http://159.75.19.163/FrequencyWords/es/es_50k.txt')
        en_res = requests.get('http://159.75.19.163/FrequencyWords/en/en_50k.txt')
        es_text = re.sub(r' \d+', '', str(es_res.text.encode('iso8859'), encoding='utf-8'))
        en_text = re.sub(r' \d+', '', str(en_res.text.encode('iso8859'), encoding='utf-8'))
        es = ['esen', 'esfr', 'espt', 'esit', 'esde', 'esca']
        en = ['enfr', 'enit', 'ende', 'ennl', 'ensv', 'enru', 'enpt', 'enpl', 'enro', 'encz', 'engr', 'entr', 'enzh',
              'enja', 'enko', 'enar']
        for lang in es:
            for word in es_text.split('\n'):
                yield response.follow(url=lang + '/' + word, callback=self.get_word, meta={'lang': lang})
        for lang in en:
            for word in en_text.split('\n'):
                yield response.follow(url=lang + '/' + word, callback=self.get_word, meta={'lang': lang})

    def get_word(self, response: HtmlResponse):
        text = response.text
        print(text)
        html = etree.HTML(text)
        key_list, val_list = [], []
        for key in html.xpath('//td[@class="FrEx"]'):
            val = key.xpath('../following-sibling::tr[1]/td[contains(@class,"ToEx")]')
            if len(val):
                key_list.append(key.xpath('string(.)'))
                val_list.append(val[0].xpath('string(.)'))
        # yield {'url': response.url, 'word': list(zip(key_list, val_list)), 'lang': response.meta['lang']}
