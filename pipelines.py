# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import json

class SpiderSteamPipeline:
    def open_spider(self, spider):
        print('file opened')
        self.file = open('items.json', 'w')

    def close_spider(self, spider):
        print('file closed')
        self.file.close()

    def process_item(self, item, spider):
        print('processing an item', item['release_date'][-3:])
        if int(item['release_date'][-3:]) >= 2000:
            line = json.dumps(ItemAdapter(item).asdict()) + "\n"
            self.file.write(line)
        return item
