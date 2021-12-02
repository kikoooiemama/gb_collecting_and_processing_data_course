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


def extract_news_links(dom_x):
    result_list = []
    # add news from bottom
    items_x = dom_x.xpath('//ul[@class="list list_type_square list_half js-module"]/li')
    for item_x in items_x:
        address_x = item_x.xpath('.//a/@href')[0]
        result_list.append(address_x)

    # add news from center
    items_x = dom_x.xpath('//div[@class="daynews__item"]')
    for item_x in items_x:
        address_x = item_x.xpath('.//a/@href')[0]
        result_list.append(address_x)

    # add main news
    address_x = dom_x.xpath('//div[@class="daynews__item daynews__item_big"]/a/@href')[0]
    result_list.append(address_x)

    return result_list


def scrapping_news_page(link_n, dom_n):
    document_news = {}
    datetime = dom_n.xpath('//span[@class ="note__text breadcrumbs__text js-ago"]/@datetime')[0]
    news_date = datetime.split('T')[0].replace('-', '/')
    news_name = dom_n.xpath('//h1[@class ="hdr__inner"]/text()')[0]
    news_source = dom_n.xpath('//span[@class="note"]/a[contains(@class,"link")]/@href')[0]

    document_news['news_source'] = news_source
    document_news['news_name'] = news_name
    document_news['news_link'] = link_n
    document_news['publication_date'] = news_date

    return document_news


# init MongoDb on Ubuntu VM.
client = MongoClient('192.168.1.76', 27017)
db = client['news']
mail_news = db.mail_news
# link must be unique
mail_news.create_index('news_link', unique=True)

news_link = 'https://news.mail.ru/'
header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                  '(XHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36'}

response = requests.get(news_link, headers=header)
dom = html.fromstring(response.text)

news_list = extract_news_links(dom)
for news_link in news_list:
    response = requests.get(news_link, headers=header)
    dom = html.fromstring(response.text)
    news_data = scrapping_news_page(news_link, dom)

    mongo_insert(mail_news, news_data)

print_all_news(mail_news)
