from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule


class WarcSpider(CrawlSpider):
    name = 'www.dbj.jp'
    allowed_domains = ['www.dbj.jp']
    start_urls = ['https://www.dbj.jp/']
    custom_settings = {
        'LOG_LEVEL': 'INFO',
        'DEPTH_LIMIT': 10,
        'ITEM_PIPELINES': {
            'UBW.pipelines.WarcWriterPipeline': 300,
        }
    }
    rules = (
        Rule(LinkExtractor(allow=r'.', deny=(r'\?',)), callback='parse_item', follow=True),
    )

    def parse_item(self, response, **kwargs):
        item = {'url': response.url, 'headers': self.convert(response.headers), 'content': response.body}
        return item

    def convert(self, data):
        if isinstance(data, bytes):
            return data.decode('ascii')
        if isinstance(data, list):
            return data.pop().decode('ascii')
        if isinstance(data, dict):
            return dict(map(self.convert, data.items()))
        if isinstance(data, tuple):
            return map(self.convert, data)
        return data
