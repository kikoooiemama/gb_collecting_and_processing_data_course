# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class JobparserItem(scrapy.Item):
    # define the fields for your item here like:

    _id = scrapy.Field()
    # Наименование вакансии
    name = scrapy.Field()
    # Ссылку на саму вакансию
    url = scrapy.Field()
    # Зарплата от
    min_salary = scrapy.Field()
    # Зарплата до
    max_salary = scrapy.Field()
    # Курс
    currency = scrapy.Field()

    salary = scrapy.Field()
