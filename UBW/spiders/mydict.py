import scrapy
from lxml import etree
import requests
from scrapy.http.response.html import HtmlResponse
import re


class MydictSpider(scrapy.Spider):
    name = 'www.mydict.uk'.replace('.', '_')
    start_urls = ['https://www.mydict.uk']
    custom_settings = {
        'CONCURRENT_REQUESTS': 2,
        'DOWNLOADER_MIDDLEWARES': {
            'UBW.middlewares.VPNMiddleware': 543,
            'UBW.middlewares.PauseMiddleware': 600,
        },
        'ITEM_PIPELINES': {
            'UBW.pipelines.KVPipeline': 300,
        },
        'COOKIES_ENABLED': False,
        'DOWNLOAD_DELAY': 1,
        'SCHEDULER': "scrapy_redis.scheduler.Scheduler",
        'DUPEFILTER_CLASS': "scrapy_redis.dupefilter.RFPDupeFilter",
        'SCHEDULER_PERSIST': True,
        'SCHEDULER_QUEUE_CLASS': 'scrapy_redis.queue.PriorityQueue',
    }

    def parse(self, response: HtmlResponse, **kwargs):
        text = requests.get('http://159.75.19.163/FrequencyWords/en/en_50k.txt').text
        text = re.sub(r' \d+', '', text)
        word_list = text.split('\n')
        for word in word_list:
            url1 = f'https://www.mydict.uk/Dictionary/English-Chinese/{word}'
            url2 = f'https://www.mydict.uk/Dictionary/English-German/{word}'
            yield response.follow(url=url1, callback=self.get_word)
            yield response.follow(url=url2, callback=self.get_word)

    def get_word(self, response: HtmlResponse):
        text = response.text
        html = etree.HTML(text)
        key_list = [re.sub(r'[\r\n\t]| {2,}', '', key.xpath('string(.)')) for key in
                    html.xpath('//div[@class="wiki"]/div[4]//li/div[2]')]
        val_list = [re.sub(r'[\r\n\t]| {2,}', '', key.xpath('string(.)')) for key in
                    html.xpath('//div[@class="wiki"]/div[4]//li/div[1]')]
        for kv in zip(key_list, val_list):
            yield {'url': response.url, 'key': kv[0], 'val': kv[1]}
