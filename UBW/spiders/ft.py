import scrapy
import re
from scrapy.http.response.html import HtmlResponse
from lxml import etree
from urllib import parse
import time


class FtSpider(scrapy.Spider):
    name = 'www.ftchinese.com'.replace('.', '_')
    start_urls = ['https://www.ftchinese.com']
    custom_settings = {
        'CONCURRENT_REQUESTS': 16,
        'DOWNLOADER_MIDDLEWARES': {
            'UBW.middlewares.OfficeMiddleware': 543
        },
        'ITEM_PIPELINES': {
            'UBW.pipelines.MongoPipeline': 300,
        },
        'COOKIES_ENABLED': False,
        'DEFAULT_REQUEST_HEADERS': {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,'
                      '*/*;q=0.8,application/signed-exchange;v=b3;q=0.9 ',
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

        },
        'REDIS_HOST': '127.0.0.1',
        'REDIS_PORT': '6379',
        'SCHEDULER': 'scrapy_redis.scheduler.Scheduler',
        'DUPEFILTER_CLASS': 'scrapy_redis.dupefilter.RFPDupeFilter',
        'SCHEDULER_PERSIST': True,
    }

    def parse(self, response: HtmlResponse, **kwargs):
        columns = {
            "/channel/china.html": "中国",
            "/channel/chinareport.html": "政经",
            "/channel/chinabusiness.html": "商业",
            "/channel/chinamarkets.html": "金融市场",
            "/channel/chinastock.html": "股市",
            "/channel/chinaproperty.html": "房地产",
            "/channel/culture.html": "社会与文化",
            "/channel/chinaopinion.html": "观点",
            "/channel/world.html": "全球",
            "/channel/usa.html": "美国",
            "/channel/uk.html": "英国",
            "/channel/asia.html": "亚太",
            "/channel/europe.html": "欧洲",
            "/channel/america.html": "美洲",
            "/channel/africa.html": "非洲",
            "/channel/economy.html": "经济",
            "/channel/globaleconomy.html": "全球经济",
            "/channel/chinaeconomy.html": "中国经济",
            "/channel/trade.html": "贸易",
            "/channel/environment.html": "环境",
            "/channel/economics.html": "经济评论",
            "/channel/markets.html": "金融市场",
            "/channel/stock.html": "股市",
            "/channel/forex.html": "外汇",
            "/channel/bond.html": "债市",
            "/channel/commodity.html": "大宗商品",
            "/channel/business.html": "商业",
            "/channel/finance.html": "金融",
            "/channel/technology.html": "科技",
            "/channel/auto.html": "汽车",
            "/channel/property.html": "高端物业",
            "/channel/agriculture.html": "农林",
            "/channel/energy.html": "能源",
            "/channel/industrials.html": "工业和采矿",
            "/channel/airline.html": "航空和运输",
            "/channel/pharma.html": "医药",
            "/channel/entertainment.html": "娱乐",
            "/channel/consumer.html": "零售和消费品",
            "/channel/media.html": "传媒和文化",
            "/channel/innovation.html": "创新经济",
            "/tag/人工智能": "人工智能",
            "/tag/数字货币": "区块链与数字货币",
            "/tag/大数据": "大数据",
            "/tag/互联网": "互联网",
            "/channel/newenergy.html": "新能源与新交通",
            "/channel/innovationother.html": "其他",
            "/column/007000062": "市值管理评论",
            "/channel/education.html": "教育",
            "/channel/preschooledu.html": "学前教育",
            "/channel/secondaryedu.html": "中小学与国际学校",
            "/channel/higheredu.html": "高等教育与海外留学",
            "/channel/businessedu.html": "商业与职场教育",
            "/channel/edureform.html": "教育改革与创新",
            "/channel/opinion.html": "观点",
            "/channel/lex.html": "Lex专栏",
            "/channel/the-a-list.html": "A-List",
            "/channel/column.html": "专栏",
            "/channel/analysis.html": "分析",
            "/channel/comment.html": "评论",
            "/channel/editorial.html": "社评",
            "/channel/book.html": "书评",
            "/channel/letter.html": "读者有话说",
            "/channel/management.html": "管理",
            "/channel/mba.html": "FT商学院",
            "/channel/career.html": "职场",
            "/channel/leadership.html": "领导力",
            "/tag/%E8%B4%A2%E5%AF%8C%E7%AE%A1%E7%90%86": "财富管理",
            "/tag/%E5%95%86%E5%8A%A1%E4%BA%92%E8%81%94": "商务互联",
            "/channel/people.html": "人物",
            "/channel/lifestyle.html": "生活时尚",
            "/channel/pursuit.html": "乐尚街",
            "/channel/wine.html": "美食与美酒",
            "/channel/taste.html": "品味",
            "/channel/travel.html": "旅行",
            "/channel/life.html": "生活话题",
            "/channel/art.html": "艺术与娱乐",
            "/channel/spend.html": "消费经",
            "/channel/money.html": "理财",
        }
        for k, v in columns.items():
            meta = {'page': 1, 'column': k, 'column_cn': v}
            yield response.follow(url=k, dont_filter=True, callback=self.get_news_list, meta=meta)

    def get_news_list(self, response: HtmlResponse):
        html = etree.HTML(response.text)
        meta = response.meta
        news_list = [href for href in html.xpath("//div[@class='item-inner']/a/@href")]
        for news in news_list:
            re_news = re.search(r".*\d+", news)
            if re_news:
                yield response.follow(url=f"https://www.ftchinese.com{re_news.group(0)}/ce?archive",
                                      callback=self.get_news, meta=meta, priority=10)
        if len(news_list) > 0:
            meta['page'] = meta['page'] + 1
            split = parse.urlsplit(response.url)
            if 'tag' in split.path:
                yield response.follow(url=split.path + f"?p={meta['page']}",
                                      dont_filter=True, callback=self.get_news_list, meta=meta)
            else:
                yield response.follow(url=split.path + f"?page={meta['page']}",
                                      dont_filter=True, callback=self.get_news_list, meta=meta)

    def get_news(self, response: HtmlResponse):
        check = []
        text = response.text
        re_title = re.search(r'(?<=>).*?(?=</h1>)', text)
        if re_title:
            title = tuple(re_title.group(0).split('<br>'))
            if len(title) == 2:
                check.append(title)
        re_abstract = re.search(r'(?<=class="story-lead").*?(?=</div>)', text)
        if re_abstract:
            abstract = tuple(re_abstract.group(0).split('<br>'))
            if len(abstract) == 2:
                check.append(abstract)
        html = etree.HTML(text)
        left = [p for p in html.xpath('//div[@class="leftp"]/p/text()')]
        right = [p for p in html.xpath('//div[@class="rightp"]/p/text()')]
        if len(left) == 0 or len(right) == 0:
            pass
        check.extend(list(zip(left, right)))
        item = {
            'url': response.url,
            'date': int(time.time() * 1000),
            'column': response.meta['column_cn'],
            'text': response.text
        }
        return item
