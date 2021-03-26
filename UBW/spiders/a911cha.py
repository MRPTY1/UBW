import scrapy
from lxml import etree
import requests
from scrapy.http.response.html import HtmlResponse
import re


class A911chaSpider(scrapy.Spider):
    name = 'danci.911cha.com'.replace('.', '_')
    start_urls = ['https://danci.911cha.com/']
    custom_settings = {
        'LOG_LEVEL': 'DEBUG',
        'CONCURRENT_REQUESTS': 8,
        'ITEM_PIPELINES': {
            'UBW.pipelines.KVPipeline': 300,
        },
        'COOKIES_ENABLED': False,
    }

    def parse(self, response: HtmlResponse, **kwargs):
        text = requests.get('http://192.168.99.18/en_50k.lang').text
        word_list = text.split('\n')
        for word in word_list:
            url = f'https://danci.911cha.com/{word}.html'
            yield response.follow(url=url, callback=self.get_word)

    def get_word(self, response: HtmlResponse):
        text = response.text
        word_list = [word for word in re.findall(r'<p[\w\W]+?</p>', text)]
        word_list = [re.sub(r'(\d+\..*?</strong><br />|&nbsp;|<span.*?</span>|<.?em>|<p.*?>|</p>)', '', word)
                     for word in word_list]
        word_list = [word for word in word_list if re.search('[\u4e00-\u9fa5]', word)]
        word_list = [word for word in word_list if re.search('<br />', word)]
        word_list = [re.sub(r'([1-9]\. |[A-Z]：)', '', word) for word in word_list]
        for word in word_list:
            kv = word.split('<br />')
            yield {'key': kv[1], 'en': kv[0]}
