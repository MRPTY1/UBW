from scrapy.cmdline import execute

if __name__ == '__main__':
    execute(['scrapy', 'crawl', 'www.cgan.net'.replace('.', '_')])
