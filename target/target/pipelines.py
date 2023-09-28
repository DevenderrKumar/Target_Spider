# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient


class TargetPipeline:

    def __init__(self):
        connection = MongoClient("localhost",
                                 27017)
        db = connection["Target"]
        self.collection = db["ProductInformationWithQuestions"]

    def process_item(self, item, spider):
        # return item
        print("item--------------- {}".format(item))
        self.collection.insert_one(dict(item))
