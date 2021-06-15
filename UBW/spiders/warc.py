from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
import logging


class WarcSpider(CrawlSpider):
    name = 'WarcSpider'

    allowed_domains = 'adguard.com'.split(',')
    start_urls = 'https://adguard.com/zh_cn/welcome.html'.split(',')

    def __init__(self, *args, **kwargs):
        logger = logging.getLogger('WarcSpider')
        logger.debug(args)
        logger.debug(kwargs)
        self.name = 'adguard.com'
        self.custom_settings = {
            'LOG_LEVEL': 'DEBUG',
            'DEPTH_LIMIT': 10,
            'ITEM_PIPELINES': {
                'UBW.pipelines.WarcWriterPipeline': 300,
            },
            'DEFAULT_REQUEST_HEADERS': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                              'Chrome/90.0.4430.212 Safari/537.36 '
            }
        }
        logger.debug({'name': self.name, 'allowed_domains': self.allowed_domains, 'start_urls': self.start_urls})
        self.rules = (Rule(LinkExtractor(allow=r'.', deny=(r'\?',)), callback='parse_item', follow=True),)
        super(WarcSpider, self).__init__()

    def parse_item(self, response):
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


if __name__ == '__main__':
    from scrapy.cmdline import execute

    execute(['scrapy', 'crawl', 'WarcSpider'])
