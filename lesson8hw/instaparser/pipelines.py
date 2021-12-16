# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient
from pymongo.collection import Collection
from instaparser.items import InstaparserItem
from instaparser.spiders.instagram import InstagramSpider


class InstaparserPipeline:

    def __init__(self):
        client = MongoClient('192.168.1.76', 27017)
        db = client['instagram']
        # сюда будем записывать юзеров и данные о их аккаунте
        self.users = db.users

    def process_item(self, item: InstaparserItem, spider: InstagramSpider):
        follow_data = {'user_id': item['f_account_id'],
                       'user_name': item['f_account_name'],
                       'user_full_name': item['f_account_full_name'],
                       'profile_pic_url': item['f_account_profile_pic_url']
                       }
        self.add_data_to_db(self.users, item, follow_data)
        return item

    def add_data_to_db(self, collection: Collection, item, data_one):
        user_id = int(item['user_id'])
        ref = {'user_id': user_id}
        user_in_db = collection.count_documents(ref)
        if user_in_db:
            if item['f_account_type'] == 'follower':
                self.add_element_to_list(collection, ref, {'followers': data_one})
            else:
                self.add_element_to_list(collection, ref, {'followings': data_one})
        else:
            document = {'user_id': user_id,
                        'user_name': item['user_name'],
                        'user_followings_n': item['user_followings_n'],
                        'user_followers_n': item['user_followers_n']
                        }
            if item['f_account_type'] == 'follower':
                document['followers'] = [data_one]
                document['followings'] = []
            else:
                document['followers'] = []
                document['followings'] = [data_one]

            collection.insert_one(document)

    def add_element_to_list(self, collection, reference, element):
        collection.update_one(reference, {'$push': element}, upsert=True)
