import re

import requests
from lxml import etree

if __name__ == '__main__':
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                             'Chrome/88.0.4324.104 Safari/537.36',
               'cookie': 'null=undefined; expire=1629302400; '
                         '17a7a7fab65b13dae9c8b417746c098d=ee77a70ceef880202d1f20c727b1d9d4; '
                         'uniqueVisitorId=3cd0bb49-cbaa-d395-6113-4ebcf8bec8b9; paywall_source=; '
                         '_ga_PDY0XG13PH=GS1.1.1612159768.1.0.1612159768.0; _ga=GA1.1.366663392.1612159769; '
                         '__cfduid=dc1aeb4cad45e6212667bf7b6c5c589511612231077; '
                         'USER_ID=36cbe5e8-01be-423d-a48b-2255ac5b21b0; USER_ID_FT=36cbe5e8-01be-423d-a48b-2255ac5b21b0; '
                         'USER_NAME=Wz6JOw; USER_NAME_FT=Wz6JOw; USER_KV=ver|202102;sex|101;cs|0;csp|1;hi|0;in|0;wf|0; '
                         'paywall=standard; paywall_expire=1629302400; '
                         'ft=FjDwFkGtm2RZo4KsjzUIjvAYtnk7AGRBdxVtK+L'
                         '/gKjAOXsxbxcBZrOnByAwBDTZsyfMSS7z42EFbUBNfrinVAtjGOk9mhgD/a0A7bABYLl0nvYjbSwbfq7bg/WTW1sWhdN'
                         '/3qBjcallxNRY+KFpqsSYpTdpCEICJ7nWqt1eI9hFCR91V/huhLCG3ewj2sJo; paywall_expire=1629302400; '
                         'paywall=standard; FTSTAT_ok_times=9; expire=1629302400; FTSTAT_ok_pages=13 '
               }
    res = requests.post(url='https://www.ftchinese.com/tag/%E5%A4%A7%E6%95%B0%E6%8D%AE?p=975', headers=headers,
                        proxies={'https': '127.0.0.1:10809'})
    print(res.headers)
    html = etree.HTML(res.text)
    news_list = [href for href in html.xpath("//div[@class='item-inner']/a/@href")]
    print(news_list)
    print(len(news_list))
    for news in news_list:
        re_news = re.search(r".*\d+", news)
        if re_news:
            print(re_news.group(0))
