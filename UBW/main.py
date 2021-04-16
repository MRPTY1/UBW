from scrapy.cmdline import execute

if __name__ == '__main__':
    execute(['scrapy', 'crawl', 'dictionary.search.yahoo.com'.replace('.', '_')])
