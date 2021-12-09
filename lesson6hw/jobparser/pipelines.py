# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient
from jobparser.items import JobparserItem
from scrapy import Spider
from pymongo.errors import DuplicateKeyError
import re


class JobparserPipeline:
    def __init__(self):
        client = MongoClient('192.168.1.76', 27017)
        self.db = client['vacancies']

    def process_item(self, item: JobparserItem, spider: Spider):
        if spider.name == 'hhru':
            final_salary = self.process_salary_hhru(item['salary'])
            item['min_salary'] = final_salary[0]
            item['max_salary'] = final_salary[1]
            item['currency'] = final_salary[2]
            del item['salary']
        elif spider.name == 'sjru':
            final_salary = self.process_salary_sjru(item['salary'])
            item['min_salary'] = final_salary[0]
            item['max_salary'] = final_salary[1]
            item['currency'] = final_salary[2]
            del item['salary']
        else:
            print(f"Информация от неизвестного паука: {spider}, {item}")

        collection = self.db[spider.name]
        self.mongo_insert(collection, item)

        return item

    def process_salary_hhru(self, salary):
        c_salary = self.clean_salary(salary)
        salary_min = None
        salary_max = None
        salary_currency = None

        if len(c_salary) > 1:
            if c_salary[0] == 'до':
                try:
                    salary_max = int(c_salary[1])
                except ValueError:
                    print(f"Не удалось распарсить: {c_salary[1]}")
                salary_currency = c_salary[2]
            elif ('до' in c_salary) and ('от' in c_salary):
                try:
                    salary_min = int(c_salary[1])
                    salary_max = int(c_salary[3])
                except ValueError:
                    print(f"Не удалось распарсить: {c_salary[1]} и {c_salary[3]}")
                salary_currency = c_salary[4]
            elif c_salary[0] == 'от':
                try:
                    salary_min = int(c_salary[1])
                except ValueError:
                    print(f"Не удалось распарсить: {c_salary[1]}")
                salary_currency = c_salary[2]
            elif '—' in c_salary:
                try:
                    salary_min = int(c_salary[0])
                    salary_max = int(c_salary[2])
                    salary_currency = c_salary[3]
                except ValueError:
                    print(f"Не удалось распарсить: {c_salary[0]},{c_salary[2]}")
            else:
                print(f"===Anomaly! Need to check!===")

        return salary_min, salary_max, salary_currency

    def process_salary_sjru(self, salary):
        c_salary = self.clean_salary(salary)
        salary_min = None
        salary_max = None
        salary_currency = None
        if len(c_salary) > 1:
            if c_salary[0] == 'до':
                try:
                    payload = c_salary[1]
                    regex_num = re.compile('[0-9]+')
                    s = regex_num.search(payload)
                    salary_max = int(payload[s.start():s.end()])
                    salary_currency = payload[s.end():]
                except ValueError:
                    print(f"Не удалось распарсить: {c_salary[1]}")
            # elif ('до' in c_salary) and ('от' in c_salary):
            #     try:
            #         salary_min = int(c_salary[1])
            #         salary_max = int(c_salary[3])
            #     except ValueError:
            #         print(f"Не удалось распарсить: {c_salary[1]} и {c_salary[3]}")
            #     salary_currency = c_salary[4]
            elif c_salary[0] == 'от':
                try:
                    payload = c_salary[1]
                    regex_num = re.compile('[0-9]+')
                    s = regex_num.search(payload)
                    salary_min = int(payload[s.start():s.end()])
                    salary_currency = payload[s.end():]
                except ValueError:
                    print(f"Не удалось распарсить: {c_salary[1]}")
            elif '—' in c_salary:
                try:
                    salary_min = int(c_salary[0])
                    salary_max = int(c_salary[2])
                    salary_currency = c_salary[3]
                except ValueError:
                    print(f"Не удалось распарсить: {c_salary[0]},{c_salary[2]}")
            elif (c_salary[0].isdigit()) and (len(c_salary) < 5):
                try:
                    salary_min = int(c_salary[0])
                    salary_max = int(c_salary[0])
                    salary_currency = c_salary[1]
                except ValueError:
                    print(f"Не удалось распарсить: {c_salary[0]}")
            else:
                print(f"===Anomaly! Need to check!===")

        return salary_min, salary_max, salary_currency

    def mongo_insert(self, collection, document):
        try:
            collection.insert_one(document)
        except DuplicateKeyError:
            print(f"Вакансия: '{document}' уже находится в базе в коллекции '{collection}'.")

    def clean_salary(self, salary_list: list):
        result = []
        for item in salary_list:
            item = item.strip().replace('\xa0', '').replace(' ', '')
            if item:
                result.append(item)
        return result
