import scrapy
from scrapy.http.response.html import HtmlResponse
from lxml import etree


class ChinadailySpider(scrapy.Spider):
    name = 'language.chinadaily.com.cn'.replace('.', '_')
    start_urls = ['http://language.chinadaily.com.cn/']
    custom_settings = {
        'CONCURRENT_REQUESTS': 8,
        'ITEM_PIPELINES': {
            'UBW.pipelines.MongoPipeline': 300,
        },
        'COOKIES_ENABLED': False
    }

    def parse(self, response: HtmlResponse, **kwargs):
        for i in range(1, 138):
            url = f'https://language.chinadaily.com.cn/news_bilingual/page_{i}.html'
            yield response.follow(url=url, callback=self.get_list)

    def get_list(self, response: HtmlResponse):
        html = etree.HTML(response.text)
        for href in html.xpath("//div[@class='gy_box']/a/@href"):
            yield response.follow(url=href, callback=self.get_text)

    def get_text(self, response: HtmlResponse):
        yield {'url': response.url, 'text': response.text}
