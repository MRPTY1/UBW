import scrapy
from scrapy.http.response.html import HtmlResponse
from lxml import etree
from urllib import parse


class UnistudySpider(scrapy.Spider):
    name = 'i.unistudy.top'.replace('.', '_')
    start_urls = ['http://i.unistudy.top/']
    custom_settings = {
        'CONCURRENT_REQUESTS': 8,
        'ITEM_PIPELINES': {
            'UBW.pipelines.MongoPipeline': 300,
        },
        'COOKIES_ENABLED': False,
        'DEFAULT_REQUEST_HEADERS': {
            'cookie': 'JSESSIONID=48DA84AAB8D82D59526629E593AE5480; '
                      'acw_tc=76b20f6516141590288258570e40b118b8f9fe6734ceb0e7916ae048efa5f7 '
        }
    }

    def parse(self, response: HtmlResponse, **kwargs):
        url = 'https://i.unistudy.top/categoryReading/category/mf/1/'
        for page in range(1, 21):
            yield response.follow(url=url + str(page), callback=self.get_list)

    def get_list(self, response: HtmlResponse):
        url1 = 'https://i.unistudy.top/buy/free/'
        url2 = 'https://edu.unistudy.top/sentencecontroller/catalog'
        html = etree.HTML(response.text)
        for href in html.xpath('//li[@class="fleft"]/a/@href'):
            yield response.follow(url=url1 + href[13:], method='post', priority=10)
            data = {'columnType': '1', 'bookid': f'{href[13:]}'}
            yield scrapy.FormRequest(url=url2, formdata=data,
                                     callback=self.get_context_list, meta={'id': f'{href[13:]}'})

    def get_context_list(self, response: HtmlResponse):
        url = 'https://edu.unistudy.top/segmentscontroller/pageTest'
        params = {
            'chapterId': '1366',
            'bookid': f'{response.meta["id"]}',
            'userid': '607271',
            'columnType': '1'
        }
        for chapter in response.json():
            params['chapterId'] = chapter['id']
            yield response.follow(url=url + '?' + parse.urlencode(params), callback=self.get_text)

    def get_text(self, response: HtmlResponse):
        limits = response.json()
        zh, en = [], []
        if limits['statusCode'] == 0:
            for limit in limits['data']:
                zh.append(limit['segment_en'])
                en.append(limit['segment_zh'])
        return {'url': response.url, 'text': list(zip(zh, en))}
