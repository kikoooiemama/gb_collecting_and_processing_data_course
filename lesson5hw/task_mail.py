# Написать программу, которая собирает входящие письма из своего или тестового почтового ящика и сложить данные о
# письмах в базу данных (от кого, дата отправки, тема письма, текст письма полный)
#
# Логин тестового ящика: study.ai_172@mail.ru
# Пароль тестового ящика: NextPassword172#


from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from pymongo.errors import DuplicateKeyError
from pymongo import MongoClient


def mongo_insert(collection, document):
    try:
        collection.insert_one(document)
    except DuplicateKeyError:
        print(f"Письмо с темой '{document['subject']}', от '{document['from']}' уже находится в базе!")


def print_all_letters(collection):
    for el in collection.find({}):
        print(f"От кого: {el['from']}\n"
              f"Тема: {el['subject']}\n"
              f"Дата: {el['date']}\n"
              # f"Текст: {el['text']}\n"
              )


# init MongoDb on Ubuntu VM.
client = MongoClient('192.168.1.76', 27017)
db = client['my_mail']
letters_mail_ru = db.letters_mail_ru

chrome_options = Options()
chrome_options.add_argument('start-maximized')
driver = webdriver.Chrome(executable_path='./chromedriver.exe', options=chrome_options)

driver.get('https://mail.ru/')
driver.implicitly_wait(3)

username = driver.find_element(By.NAME, 'login')
username.send_keys('study.ai_172@mail.ru')
username.send_keys(Keys.ENTER)

password = driver.find_element(By.NAME, 'password')
password.send_keys('NextPassword172#')
password.send_keys(Keys.ENTER)

# empty set, set doesnt have duplications.
letter_urls = set()

time.sleep(1)

while True:
    actions = ActionChains(driver)
    letters_a = driver.find_elements(By.XPATH, "//div[@class='dataset__items']/a")
    if letters_a[-1].get_attribute('href') in letter_urls:
        break
    for letter_a in letters_a:
        time.sleep(0.02)
        letter_url = letter_a.get_attribute('href')
        letter_urls.add(letter_url)

    # scrolling
    time.sleep(0.02)
    actions.move_to_element(letters_a[-1])
    actions.perform()

letter_urls -= {None}

# add to db
for url in letter_urls:
    mail_letter = {}
    driver.get(url)

    mail_from = driver.find_element(By.XPATH, "//span[@class='letter-contact']").get_attribute('title')
    mail_subject = driver.find_element(By.CLASS_NAME, 'thread__subject').text
    mail_date = driver.find_element(By.CLASS_NAME, 'letter__date').text
    mail_text = driver.find_element(By.XPATH, "//div[@class='letter__body']").text

    mail_letter['_id'] = url
    mail_letter['from'] = mail_from
    mail_letter['subject'] = mail_subject
    mail_letter['date'] = mail_date
    mail_letter['text'] = mail_text

    mongo_insert(letters_mail_ru, mail_letter)

# close driver/browser
driver.close()

# print
# print_all_letters(letters_mail_ru)
