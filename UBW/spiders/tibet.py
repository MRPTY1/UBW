import scrapy
from scrapy.http.response.html import HtmlResponse
from lxml import etree
import re
import os
import requests


class TibetSpider(scrapy.Spider):
    name = 'www.tibet.cn'.replace('.', '_')
    start_urls = ['http://www.tibet.cn/']
    custom_settings = {
        'CONCURRENT_REQUESTS': 8,
        'DOWNLOADER_MIDDLEWARES': {
            'UBW.middlewares.RandomProxiesMiddleware': 544,
        },
        'ITEM_PIPELINES': {
            'UBW.pipelines.MongoPipeline': 300,
        },
        'COOKIES_ENABLED': False,
    }

    def parse(self, response: HtmlResponse, **kwargs):
        url_dict = {'http://www.tibet.cn/cn/news/': '新闻',
                    'http://www.tibet.cn/cn/politics/': '时政',
                    'http://www.tibet.cn/cn/bwsp/': '时评',
                    'http://www.tibet.cn/cn/culture/': '文化',
                    'http://www.tibet.cn/cn/aid_tibet/': '援藏',
                    'http://www.tibet.cn/cn/travel/': '旅游',
                    'http://www.tibet.cn/cn/rediscovery/': '文史',
                    'http://www.tibet.cn/cn/tech/': '科技',
                    'http://www.tibet.cn/cn/book/': '读书',
                    'http://www.tibet.cn/cn/data/': '数据',
                    'http://www.tibet.cn/cn/edu/': '教育',
                    'http://www.tibet.cn/cn/ecology/': '生态',
                    'http://www.tibet.cn/cn/fp/': '扶贫',
                    'http://www.tibet.cn/cn/network/': '动态', }
        for url, title in url_dict.items():
            yield response.follow(url=url, callback=self.get_index, meta={'title': title})

    def get_index(self, response: HtmlResponse):
        meta = {'title': response.meta['title']}
        text = response.text
        html = etree.HTML(text)
        for href in html.xpath('//div[contains(@class,"listnews")]//h4/a/@href'):
            yield response.follow(url=href, callback=self.get_word, meta=meta)
        last_page = re.search(r'(?<=createPageHTML\()\d+', text)
        if last_page:
            last_page = last_page.group(0)
            for i in range(1, int(last_page) + 1):
                yield response.follow(url=response.url + f'index_{i}.html', callback=self.get_list, meta=meta)

    def get_list(self, response: HtmlResponse):
        meta = {'title': response.meta['title']}
        text = response.text
        html = etree.HTML(text)
        for href in html.xpath('//div[contains(@class,"listnews")]//h4/a/@href'):
            yield response.follow(url=href, callback=self.get_word, meta=meta)

    def get_word(self, response: HtmlResponse):
        text = response.text
        html = etree.HTML(text)
        title = response.meta['title']
        path = 'D:/www.tibet.cn/'
        if not os.path.exists(f'{path}{title}'):
            os.mkdir(f'{path}{title}')
        file_name = html.xpath('string(//div[@class="title_box"]/h2)')
        file_text = html.xpath("string(//div[@class='TRS_Editor'])")
        with open(f'{path}{title}/{file_name}.txt', 'w+', encoding='utf-8') as file:
            file.write(file_text)
        return {'url': response.url, 'title': title, 'name': file_name, 'text': file_text}
