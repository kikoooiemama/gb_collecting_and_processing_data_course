# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class InstaparserItem(scrapy.Item):
    # относится к подписчику/подписке
    f_account_full_name = scrapy.Field()
    f_account_name = scrapy.Field()
    f_account_id = scrapy.Field()
    f_account_profile_pic_url = scrapy.Field()
    f_account_type = scrapy.Field()

    user_id = scrapy.Field()
    user_name = scrapy.Field()
    user_followings_n = scrapy.Field()
    user_followers_n = scrapy.Field()