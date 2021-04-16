import scrapy
from scrapy.http.response.html import HtmlResponse
from lxml import etree
import re
import requests


class JalawtranslationSpider(scrapy.Spider):
    name = 'www.japaneselawtranslation.go.jp.new'.replace('.', '_')
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
        text = requests.get('http://192.168.99.18/ja_full.lang').text
        word_list = text.split('\n')
        for word in word_list:
            url = f'http://www.japaneselawtranslation.go.jp/law/list/?ft=1&re=01&dn=1&ky={word}&co=01&ia=03&ja=04'
            yield response.follow(url=url, callback=self.get_page, meta={'word': word})

    def get_page(self, response: HtmlResponse):
        text = response.text
        re_page = re.search(r'(\d+)件中　1～20件を表示', text)
        if re_page:
            page_sum = int(re_page.group(1)) // 200
            for page in range(1, page_sum + 2):
                url = 'http://www.japaneselawtranslation.go.jp/law/viewList/?' \
                      f'dn=4&x=20&y=13&ft=1&re=01&ky={response.meta["word"]}&co=01&ia=03&ja=04&page={page}'
                yield response.follow(url=url, callback=self.get_list, priority=2)

    def get_list(self, response: HtmlResponse):
        text = response.text
        html = etree.HTML(text)
        for url in html.xpath('//div[@id="keyCorner"]//li/a/@href'):
            url = re.sub(r'[ |\n]', '', url)
            yield response.follow(url=url, callback=self.get_url, priority=5)

    def get_url(self, response: HtmlResponse):
        text = response.text
        html = etree.HTML(text)
        for url in html.xpath('//iframe[@class="contents"]/@src'):
            url = re.sub(r'amp;', '', url)
            url = re.sub(r'vm=.*?&', 'vm=03&', url)
            yield response.follow(url=url, callback=self.get_word, priority=10)

    def get_word(self, response: HtmlResponse):
        text = re.sub('[\r\n]|<span.*?</span>', '', response.text)
        html = etree.HTML(text)
        key_list = [re.sub(r' {2,}', '', key.xpath('string(.)')) for key in html.xpath('/html/body/div/table/tr/td[1]')]
        val_list = [re.sub(r' {2,}', '', val.xpath('string(.)')) for val in html.xpath('/html/body/div/table/tr/td[2]')]
        for kv in zip(key_list, val_list):
            pass
            yield {'key': kv[0], 'val': kv[1]}
