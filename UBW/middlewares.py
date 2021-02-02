import random


class V2rayNMiddleware:

    def process_request(self, request, spider):
        request.meta['proxy'] = 'https://127.0.0.1:10809'


class ProxiesMiddleware:

    def process_request(self, request, spider):
        if random.getrandbits(1):
            request.meta['proxy'] = 'https://159.75.19.163:10086'
