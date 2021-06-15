import requests

if __name__ == '__main__':
    url = 'http://192.168.99.13:6800/schedule.json'
    admin = 'https://www.minitab.com/'
    lang_list = ["en-us", "fr-fr", "de-de", "pt-br", "es-mx", "ja-jp", "ko-kr", "zh-cn"]
    start_urls = ''
    for lang in lang_list:
        start_urls = f'{start_urls},{admin + lang}'
    data = {
        'project': 'WarcSpider',
        'spider': 'WarcSpider',
        'jobid': 'docwiki.embarcadero.com',
        '_name': 'docwiki.embarcadero.com',
        'allowed_domains': 'docwiki.embarcadero.com',
        'start_urls': f'http://docwiki.embarcadero.com/',
        # '_version': '2021-05-19T13_57_50' # vpn
        '_version': '2021-05-19T17_17_19'  # 过滤请求带参数的网页
    }
    res = requests.post(url=url, data=data)
    print(res.status_code)
    print(res.text)
