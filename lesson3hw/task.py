# Задание №1.
# Развернуть у себя на компьютере/виртуальной машине/хостинге MongoDB и реализовать функцию, которая будет добавлять
# только новые вакансии/продукты в вашу базу.

# Задание №2.
# Написать функцию, которая производит поиск и выводит на экран вакансии с заработной платой больше введённой суммы
# (необходимо анализировать оба поля зарплаты). Для тех, кто выполнил задание с Росконтролем - напишите запрос для
# поиска продуктов с рейтингом не ниже введенного или качеством не ниже введенного (то есть цифра вводится одна, а
# запрос проверяет оба поля)

import requests
from pprint import pprint
import re
from bs4 import BeautifulSoup
from pymongo import MongoClient


# №1. Добавление только новых вакансий в базу
def mongo_insert(collection, document):
    # DeprecationWarning: count is deprecated. Use Collection.count_documents instead.
    duplicate_check = collection.count_documents({'_id': document['_id']})
    if not duplicate_check:
        collection.insert_one(document)
        # print(f"Добавлена новая вакансия '{document['name']}', id:{document['_id']}")
    else:
        print(f"Вакансия '{document['name']}' с id:{document['_id']} уже находится в базе!")


# №2. Поиск вакансии с зп выше заданной.
def find_salaries_gt(collection, max_salary):
    print(f"\nВывод вакансий с ЗП > {max_salary} руб.")
    count = 0
    for f_v in collection.find({'$or': [{'salary_max': {'$gt': max_salary}}, {'salary_min': {'$gt': max_salary}}]}):
        count += 1
        pprint(f_v)
    print(f"\nВсего таких вакансий: {count}")


# Подключение к MongoDB. Создание коллекции
client = MongoClient('192.168.1.76', 27017)
db = client['hh']
vacancies_hh = db.vacancies_hh

# Скрапинг и добавление в базу.
# Поиск по России. area = 113
# https://hh.ru/search/vacancy?clusters=true&ored_clusters=true&enable_snippets=true&salary=&text=Data+scientist&area=113&items_on_page=20&page=33
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/96.0.4664.45 Safari/537.36'
}
link_hh = 'https://hh.ru/search/vacancy'
required_vacancy = 'Data scientist'

n_page = 0
while True:
    # vacancy = vacancy.replace(' ', '+')
    params = {
        'clusters': 'true',
        'ored_clusters': 'true',
        'enable_snippets': 'true',
        'salary': '',
        'text': required_vacancy,
        'area': 113,
        'items_on_page': 20,
        'page': n_page
    }

    response = requests.get(link_hh, params=params, headers=headers)

    if response.status_code == 200:
        dom = BeautifulSoup(response.text, 'html.parser')

        vacancy_list = dom.find_all('div', {'class': 'vacancy-serp-item__row vacancy-serp-item__row_header'})

        for vacancy in vacancy_list:
            vacancy_data = {}
            vacancy_name = vacancy.find('a').text
            vacancy_link = vacancy.find('a')['href']
            vacancy_salary = vacancy.find('span', {'data-qa': 'vacancy-serp__vacancy-compensation'})
            regex_num = re.compile('\d+')
            s = regex_num.search(vacancy_link)
            vacancy_id = vacancy_link[s.start():s.end()]

            if not vacancy_salary:
                salary_min = None
                salary_max = None
                salary_currency = None
            else:
                vacancy_salary = vacancy_salary.getText().replace(u'\xa0', u'')
                vacancy_salary = re.split(r'\s|-', vacancy_salary)
                if vacancy_salary[0] == 'до':
                    salary_min = None
                    if len(vacancy_salary) > 2:
                        if vacancy_salary[1].isdigit() and vacancy_salary[2].isdigit():
                            salary_max = float(vacancy_salary[1] + vacancy_salary[2])
                        else:
                            salary_max = float(vacancy_salary[1])
                    else:
                        salary_max = float(vacancy_salary[1])
                elif vacancy_salary[0] == 'от':
                    salary_max = None
                    salary_min = float(vacancy_salary[1])
                    if len(vacancy_salary) > 2:
                        if vacancy_salary[1].isdigit() and vacancy_salary[2].isdigit():
                            salary_min = float(vacancy_salary[1] + vacancy_salary[2])
                        else:
                            salary_min = float(vacancy_salary[1])
                    else:
                        salary_min = float(vacancy_salary[1])
                else:
                    salary_min = float(vacancy_salary[0] + vacancy_salary[1])
                    salary_max = float(vacancy_salary[3] + vacancy_salary[4])

                if not vacancy_salary[-1].isdigit():
                    salary_currency = vacancy_salary[-1]
                else:
                    salary_currency = None

            vacancy_data['_id'] = int(vacancy_id)
            vacancy_data['name'] = vacancy_name
            vacancy_data['vacancy_link'] = vacancy_link
            vacancy_data['salary_min'] = salary_min
            vacancy_data['salary_max'] = salary_max
            vacancy_data['salary_currency'] = salary_currency

            mongo_insert(vacancies_hh, vacancy_data)

        if dom.find(text='дальше'):
            n_page += 1
        else:
            break
    else:
        print(f"Остановка скрапинга на странице: {n_page}; Статус код: {response.status_code}")

# Вывести все вакансии с ЗП > 120000
find_salaries_gt(vacancies_hh, 120000)
