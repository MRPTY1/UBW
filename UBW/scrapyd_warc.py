import requests

if __name__ == '__main__':
    url = 'http://192.168.137.1:6800/schedule.json'
    data = {
        'project': 'WarcSpider',
        'spider': 'WarcSpider',
        'jobid': '2021-05-11T16_18_24',
        '_name': 'www.canyon.com',
        'allowed_domains': 'www.canyon.com',
        'start_urls': 'https://www.canyon.com/',
        # 'proxies': 'Selenium',
    }
    res = requests.post(url=url, data=data)
    print(res.status_code)
    print(res.text)
