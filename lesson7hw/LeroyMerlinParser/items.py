# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.selector import Selector
from scrapy.loader.processors import MapCompose, TakeFirst


def price_to_digit(value):
    if value:
        value = value.replace(',', '.').replace(' ', '')
        try:
            return float(value)
        except ValueError:
            return value


def process_properties(value):
    if value:
        r = Selector(text=value)
        sel_list = r.xpath('//div[@class = "def-list__group"]')
        result = {}
        for sel in sel_list:
            # название свойства
            k = sel.xpath('.//dt/text()').extract_first()
            # обработка значения свойства
            v_str = sel.xpath('.//dd/text()').extract_first()
            v_str = ''.join(i.strip().replace(',', '.') for i in v_str.split('\n'))
            try:
                v = float(v_str)
            except ValueError:
                v = v_str
            result[k] = v
        value = result
        return value


class LeroymerlinparserItem(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field(output_processor=TakeFirst())
    link = scrapy.Field(output_processor=TakeFirst())
    price = scrapy.Field(input_processor=MapCompose(price_to_digit), output_processor=TakeFirst())
    props = scrapy.Field(input_processor=MapCompose(process_properties), output_processor=TakeFirst())
    photos = scrapy.Field()
    _id = scrapy.Field()
