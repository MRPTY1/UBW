from scrapy.cmdline import execute

if __name__ == '__main__':
    execute(['scrapy', 'crawl', 'i.unistudy.top'.replace('.', '_')])
