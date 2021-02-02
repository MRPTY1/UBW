import pymongo
from pymongo.errors import DuplicateKeyError
from io import BytesIO
from warcio import WARCWriter, StatusAndHeaders


class MongoPipeline:

    def open_spider(self, spider):
        self.my_cli = pymongo.MongoClient('mongodb://127.0.0.1:27017')
        self.my_table = self.my_cli['spider_data'][f'{spider.name}']
        self.my_table.create_index([('url', 1)], unique=True)

    def close_spider(self, spider):
        self.my_cli.close()
        pass

    def process_item(self, item, spider):
        try:
            self.my_table.insert_one(dict(item))
        except DuplicateKeyError:
            pass


class WarcWriterPipeline:

    def open_spider(self, spider):
        self.output = open(f'D:/{spider.name}.warc.gz', 'wb')

    def close_spider(self, spider):
        self.output.close()

    def process_item(self, item, spider):
        writer = WARCWriter(self.output, gzip=True)
        headers_list = item['headers']

        http_headers = StatusAndHeaders('200 OK', headers_list, protocol='HTTP/1.0')

        record = writer.create_warc_record(item['url'], 'response',
                                           payload=BytesIO(item['content']),
                                           http_headers=http_headers)

        writer.write_record(record)
