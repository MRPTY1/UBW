import scrapy
from scrapy.http.response.html import HtmlResponse
from lxml import etree
import re


class ChinadailySpider(scrapy.Spider):
    name = 'language.chinadaily.com.cn'.replace('.', '_')
    start_urls = ['http://language.chinadaily.com.cn/']
    custom_settings = {
        'CONCURRENT_REQUESTS': 16,
        'ITEM_PIPELINES': {
            'UBW.pipelines.MongoPipeline': 300,
        },
        'COOKIES_ENABLED': False
    }

    def parse(self, response: HtmlResponse, **kwargs):
        columns = ['news_bilingual', 'news_hotwords', 'trans_collect', 'trans_experience']
        for column in columns:
            url = f'https://language.chinadaily.com.cn/{column}/'
            yield response.follow(url=url, callback=self.get_max_list)

    def get_max_list(self, response: HtmlResponse):
        html = etree.HTML(response.text)
        for href in html.xpath("//div[@id='div_currpage']/a[last()]/@href"):
            re_page = re.search(r'(?<=page_)\d+', href)
            if not (re_page is None):
                for page in range(1, int(re_page.group(0)) + 1):
                    yield response.follow(url=response.url + f'page_{page}.html', callback=self.get_list)

    def get_list(self, response: HtmlResponse):
        html = etree.HTML(response.text)
        for href in html.xpath("//div[@class='gy_box']/a/@href"):
            yield response.follow(url=href, callback=self.get_text)

    def get_text(self, response: HtmlResponse):
        yield {'url': response.url, 'text': response.text}
