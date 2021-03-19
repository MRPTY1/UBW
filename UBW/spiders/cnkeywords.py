import requests
import scrapy
from scrapy.http.response.html import HtmlResponse
import re
from lxml import etree
import os


class CnkeywordsSpider(scrapy.Spider):
    name = 'www.cnkeywords.net'.replace('.', '_')
    start_urls = ['http://www.cnkeywords.net/']
    lang_list = ["zh", "en", "fr", "ru", "de", "es", "pt", "ar", "ja", "ko", "bo", "ug", "mn"]
    custom_settings = {
        'CONCURRENT_REQUESTS': 32,
        'ITEM_PIPELINES': {
            'UBW.pipelines.MongoPipeline': 300,
        },
        'DOWNLOADER_MIDDLEWARES': {
            'UBW.middlewares.ProxiesMiddleware': 543
        },
        'COOKIES_ENABLED': False,
        'SCHEDULER': "scrapy_redis.scheduler.Scheduler",
        'DUPEFILTER_CLASS': "scrapy_redis.dupefilter.RFPDupeFilter",
        'SCHEDULER_PERSIST': True,
        'SCHEDULER_QUEUE_CLASS': 'scrapy_redis.queue.PriorityQueue',
    }

    def parse(self, response: HtmlResponse, **kwargs):
        url = 'https://www.cnkeywords.net/search?content='
        text = requests.get('http://192.168.99.18/en_50k.lang').text
        for key in text.split('\n'):
            if len(key):
                yield response.follow(url=url + key, callback=self.get_list)

    def get_list(self, response: HtmlResponse):
        text = response.text
        re_number = re.search(r'(?<=共有)\d+(?=条搜索结果)', text)
        if re_number is None:
            return
        html = etree.HTML(text)
        url_list = [url for url in html.xpath('//div[@class="con-page-txt content"]/@onclick')]
        url_list2 = [url for url in html.xpath('//div[@class="mail-item"]/@onclick')]
        url_list = url_list + url_list2
        for url in url_list:
            _id = re.search('[a-z0-9]{32}', url)
            if _id:
                for lang in self.lang_list:
                    url = 'https://www.cnkeywords.net/vocabulary/chengeCabularyLang'
                    data = {
                        'wordId': f'{_id.group(0)}',
                        'vocabularyLang': f'{lang}',
                        'curentlang': 'zh'
                    }
                    meta = {
                        'url': f'https://www.cnkeywords.net/vocabulary/toVocabulary?wordId={_id.group(0)}&lang={lang}'
                    }
                    yield scrapy.FormRequest(url=url, formdata=data, callback=self.get_context, priority=10,
                                             method='post', meta=meta)
        if 'fPageNo' not in response.url:
            number = int(re_number.group(0))
            for page in range(1, int(number / 8) + 2):
                yield response.follow(url=response.url + f'&fPageNo={page}', callback=self.get_list, priority=5)

    def get_context(self, response: HtmlResponse):
        return {'url': response.meta['url'], 'text': response.text}
