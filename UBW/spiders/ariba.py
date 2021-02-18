import scrapy
from scrapy.http.response.html import HtmlResponse
from urllib import parse
from lxml import etree


class AribaSpider(scrapy.Spider):
    name = 'uex.ariba.com'.replace('.', '_')
    start_urls = ['https://ariba.com']
    custom_settings = {
        'CONCURRENT_REQUESTS': 16,
        'ITEM_PIPELINES': {
            'UBW.pipelines.WarcWriterPipeline': 300,
        },
        'COOKIES_ENABLED': False,
        'DEFAULT_REQUEST_HEADERS': {
            'Cookie': 'session_api_session=hJYxyCzUKGFAUaTLpln1bQn3Rlr_DfIeY6edxhsOn_I; '
                      'AMCV_B68602BE5330943C0A490D4C@AdobeOrg=-1124106680|MCIDTS|18677|MCMID'
                      '|90275362290560432056319381010408850986|MCOPTOUT-1613623702s|NONE|vVersion|5.2.0; '
                      'mbox=session#8eeed2a8b60b407c9e46605220dc008c#1613618364|PC#8eeed2a8b60b407c9e46605220dc008c'
                      '.38_0#1676861306; ROUTEID=.5; spotlightKeys={"snapshot":"SNAP-2689405","spotlight_keys":[0]}; '
                      'c_user_session=r6Ge-UX3guGLznlHLRlqm2Ua5DACugPMp8TIRQk4RkU~; a_fenb=is; auc_ctxt_tag_list={'
                      '"app":"profilemanagement","page":"ariba_network_service_apps_profilemanagement_pmhome"}; '
                      'SSESSf5a816e3cc4b00d9e0d82cbdeae75648=cAvVGnVMy66jzkDnflSLfVn-S6oaan83rToqsPhzlh8; has_js=1 '
        }
    }

    def parse(self, response: HtmlResponse, **kwargs):
        url = 'https://uex.ariba.com/auc/front'
        params = {
            'a_lang': 'en',
            'page': '',
        }
        for i in range(0, 477):
            if i == 0:
                yield response.follow(url=url, callback=self.get_list)
                continue
            params['page'] = str(i)
            url_params = parse.urlencode(params)
            yield response.follow(url=url + '?' + url_params, callback=self.get_list)

    def get_list(self, response: HtmlResponse):
        languages = ['bg', 'zh-cn', 'zh-tw', 'hr', 'cs', 'da', 'nl', 'en', 'fi', 'fr', 'de', 'el', 'hu', 'it', 'ja',
                     'ko',
                     'no', 'pl', 'pt-br', 'ro', 'ru', 'es', 'sv', 'th', 'tr']
        text = response.text
        html = etree.HTML(text)
        for href in html.xpath("//div[@class='teaser-title-wrap']/a/@href"):
            for lang in languages:
                url = href + '?' + f'a_lang={lang}'
                yield response.follow(url=url, meta={'url': url}, callback=self.get_context)

    def get_context(self, response: HtmlResponse):
        item = {
            'url': response.meta['url'],
            'headers': self.convert(response.headers),
            'content': response.body
        }
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
