import csv
import pymongo
import time

class Pipeline():
    head = ['channel_id', 'channel_name','location','subscribe',
            'videos_info', 'contacts', 'channel_url']

    def __init__(self):
        self.f = open("youtube-{}.csv".format(time.time()),
                      "w", newline="", encoding='utf-8')
        self.fieldnames = self.head
        self.writer = csv.DictWriter(self.f, fieldnames=self.fieldnames)
        self.writer.writeheader()

    def write(self, item):
        self.writer.writerow(item)

class YouTubeMongoP(object):

    def __init__(self):
        self.client = pymongo.MongoClient('localhost')
        self.db = self.client.get_database('youtube')
        # self.collection = self.db.get_collection('youtube_users')
        self.collection = self.db.get_collection('youtube_users_2')
    
    def check_name(self,item):
        result = self.collection.find_one({"nickname": item})
        if result:
            return True
        else:
            return False
    
    def check(self,item):
        result = self.collection.find_one({"youtube_link": item})
        if result:
            return True
        else:
            return False

    def process_item(self, item):
        result = self.collection.find_one_and_replace({"youtube_link": item['youtube_link']}, dict(item))
        if not result:
            insert_result = self.collection.insert_one(dict(item))
        return item
