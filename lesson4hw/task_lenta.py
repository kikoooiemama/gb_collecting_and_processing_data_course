# Задание №1. Написать приложение, которое собирает основные новости с сайта на выбор news.mail.ru, lenta.ru,
# yandex-новости. Для парсинга использовать XPath. Структура данных должна содержать:
#   - название источника;
#   - наименование новости;
#   - ссылку на новость;
#   - дата публикации.

# Задание №2. Сложить собранные новости в БД


from lxml import html
import requests
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
import re


def mongo_insert(collection, document):
    try:
        collection.insert_one(document)
    except DuplicateKeyError:
        print(f"Новость '{document['news_name']}' | '{document['news_link']}' уже находится в базе!")


def print_all_news(collection):
    for news in collection.find({}):
        print(f"Название источника: {news['news_source']}\n"
              f"Наименование новости: {news['news_name']}\n"
              f"Ссылка: {news['news_link']}\n"
              f"Дата публикации: {news['publication_date']}\n")


# init MongoDb on Ubuntu VM.
client = MongoClient('192.168.1.76', 27017)
db = client['news']
lenta_news = db.lenta_news
# link must be unique
lenta_news.create_index('news_link', unique=True)

news_link = 'https://lenta.ru'
header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                  '(XHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36'}

response = requests.get(news_link, headers=header)
dom = html.fromstring(response.text)

# add news from column 'Main news'
items = dom.xpath('//div[@class = "b-yellow-box__wrap"]/div[@class = "item"]')
for item in items:
    news_data = {}
    news_name = item.xpath('.//a/text()')
    news_name = " ".join(news_name[0].split())
    link_raw = item.xpath('.//a/@href')
    link = news_link + link_raw[0]
    news_date = '/'.join(link_raw[0].split('/')[2:5])

    news_data['news_source'] = news_link
    news_data['news_name'] = news_name
    news_data['news_link'] = link
    news_data['publication_date'] = news_date

    mongo_insert(lenta_news, news_data)

# add news from center
cols = dom.xpath('//div[@class="span4"]')
for col in cols[:2]:
    items = col.xpath('./div[contains(@class, "item")]')
    for item in items:
        news_data = {}
        news_name = item.xpath('.//a/text()')
        news_name = " ".join(news_name[0].split())
        link_raw = item.xpath('.//a/@href')[0]
        # moslenta and other sources
        if link_raw.startswith('https://'):
            link = link_raw
            regex_num = re.compile('\\d+-\\d+-\\d+')
            s = regex_num.search(link_raw)
            date_raw = link_raw[s.start():s.end()]
            date_raw = date_raw.split('-')
            news_date = date_raw[2] + '/' + date_raw[1] + '/' + date_raw[0]
            news_source = 'https://' + link_raw.split('/')[2]
        # lenta.ru
        else:
            link = news_link + link_raw
            news_date = '/'.join(link_raw.split('/')[2:5])
            news_source = news_link

        news_data['news_source'] = news_source
        news_data['news_name'] = news_name
        news_data['news_link'] = link
        news_data['publication_date'] = news_date

        mongo_insert(lenta_news, news_data)

print_all_news(lenta_news)
