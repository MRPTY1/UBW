import random
import scrapy


class V2rayNMiddleware:

    def process_request(self, request, spider):
        request.meta['proxy'] = 'https://127.0.0.1:10809'


class ProxiesMiddleware:

    def process_request(self, request, spider):
        if 'https' in request.url:
            request.meta['proxy'] = 'https://159.75.19.163:10086'
        else:
            request.meta['proxy'] = 'http://159.75.19.163:10086'


class RandomProxiesMiddleware:

    def process_request(self, request, spider):
        if random.getrandbits(1):
            if 'https' in request.url:
                request.meta['proxy'] = 'https://159.75.19.163:10086'
            else:
                request.meta['proxy'] = 'http://159.75.19.163:10086'


class SeleniumInterceptMiddleware:

    def process_request(self, request, spider):
        spider.chrome.get(request.url)
        return scrapy.http.HtmlResponse(url=spider.chrome.current_url, body=spider.chrome.page_source,
                                        encoding='utf-8', request=request, status=200)
