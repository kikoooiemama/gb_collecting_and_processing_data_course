# Вариант 1. Необходимо собрать информацию о вакансиях на вводимую должность (используем input или через аргументы
# получаем должность) с сайтов HH(обязательно) и/или Superjob(по желанию). Приложение должно анализировать несколько
# страниц сайта (также вводим через input или аргументы). Получившийся список должен содержать в себе минимум:

# 1. Наименование вакансии.
# 2. Предлагаемую зарплату (разносим в три поля: минимальная и максимальная и валюта. цифры преобразуем к цифрам).
# 3. Ссылку на саму вакансию.
# 4. Сайт, откуда собрана вакансия.

# По желанию можно добавить ещё параметры вакансии (например, работодателя и расположение). Структура должна быть
# одинаковая для вакансий с обоих сайтов. Общий результат можно вывести с помощью dataFrame через pandas.
# Сохраните в json либо csv.
import numpy as np
from bs4 import BeautifulSoup as bs
import requests
import re
import pandas as pd


def parsing_vacancies(profession, page):
    vacancies = []
    url = 'https://hh.ru/search/vacancy'
    params = {
        'text': profession,
        'search_field': 'name',
        'items_on_page': '100',
        'page': page,
    }
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/96.0.4664.45 Safari/537.36'
    }

    html = requests.get(url, params=params, headers=headers)
    if html.ok:
        parsed_html = bs(html.text, 'html.parser')
        found_vacancies = parsed_html.find('div', {'data-qa': 'vacancy-serp__results'}).find_all('div', {
            'class': 'vacancy-serp-item'})
        for f_vacancy in found_vacancies:
            vacancies.append(parsing_vacancy(f_vacancy))

    return vacancies


def parsing_vacancy(f_vacancy):
    vacancies = {}

    # Название
    vacancy_name = f_vacancy.find('div', {'class': 'vacancy-serp-item__info'}).getText()
    vacancies['vacancy_name'] = vacancy_name

    # Зп
    salary = f_vacancy.find('div', {'class': 'vacancy-serp-item__sidebar'})
    salary_min = None
    salary_max = None
    salary_currency = None
    if salary:
        salary = salary.getText().replace(u'\u202f', u'')
        salary = re.split(r'\s|-', salary)
        if len(salary) > 1:
            if salary[0] == 'до':
                try:
                    salary_max = int(salary[1])
                except ValueError:
                    print(f"Не удалось распарсить: {salary[1]}")
                salary_currency = salary[2]
            elif salary[0] == 'от':
                try:
                    salary_min = int(salary[1])
                except ValueError:
                    print(f"Не удалось распарсить: {salary[1]}")
                salary_max = None
                salary_currency = salary[2]
            else:
                try:
                    salary_min = int(salary[0])
                    salary_max = int(salary[2])
                    salary_currency = salary[3]
                except ValueError:
                    print(f"Не удалось распарсить: {salary[0]},{salary[2]}")

    vacancies['salary_min'] = salary_min
    vacancies['salary_max'] = salary_max
    vacancies['salary_currency'] = salary_currency

    # Ссылка
    vacancy_link = f_vacancy.find('div', {'class': 'vacancy-serp-item__info'}).find('a')['href']
    vacancies['link'] = vacancy_link

    # Сайт
    vacancies['site'] = 'www.hh.ru'

    return vacancies


def parsing_hh(profession, page):
    vacancies = []
    vacancies.extend(parsing_vacancies(profession, page))
    result_df = pd.DataFrame(vacancies)
    result_df.index = np.arange(1, len(result_df) + 1)

    return result_df


# Скрипт
n_page = 4
vacancy = 'Программист'
vacancies_df = parsing_hh(vacancy, n_page)
print(vacancies_df.to_string())

# Запись в файл
vacancies_df.to_csv('vacancies.csv', sep=";", index=False)
