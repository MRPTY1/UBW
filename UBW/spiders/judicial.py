import scrapy
from scrapy.http.response.html import HtmlResponse
from urllib.parse import urlencode
from lxml import etree
import re


class JudicialSpider(scrapy.Spider):
    name = 'law.judicial.gov.tw'.replace('.', '_')
    start_urls = ['https://baidu.com/']
    custom_settings = {
        'CONCURRENT_REQUESTS': 4,
        'DOWNLOADER_MIDDLEWARES': {
            'UBW.middlewares.V2rayNMiddleware': 543,
        },
        'ITEM_PIPELINES': {
            'UBW.pipelines.MongoPipeline': 300,
        },
        'COOKIES_ENABLED': False,
    }

    def parse(self, response: HtmlResponse, **kwargs):
        url = 'https://law.judicial.gov.tw/FLAW/qryresultlst.aspx'
        gcs = {'01': 1, '02': 21, '03': 25, '04': 25}
        params = {
            'ty': 'N',
            'q': '07b3307a05ceb2c0588e897d9e43fae5',
            'gy': 'pcode',
        }
        for gc, page in gcs.items():
            for i in range(1, page + 1):
                params['gc'] = gc
                params['page'] = i
                yield response.follow(url=url + '?' + urlencode(params), callback=self.get_list)

    def get_list(self, response: HtmlResponse, **kwargs):
        text = response.text
        html = etree.HTML(text)
        for trs in html.xpath("//tr"):
            if len(trs.xpath('td/a[@id="hlEn"]')) == 1 and len(trs.xpath('td/a[@id="hlLawName"]')) == 1:
                yield response.follow(url=trs.xpath('td/a[@id="hlEn"]/@href')[0], callback=self.get_word, priority=10)
                yield response.follow(url=trs.xpath('td/a[@id="hlLawName"]/@href')[0], callback=self.get_word,
                                      priority=10)

    def get_word(self, response: HtmlResponse, **kwargs):
        return {'url': response.url, 'text': response.text}
