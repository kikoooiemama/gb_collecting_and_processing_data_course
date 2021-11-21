# Задание №2. Изучить список открытых API (https://www.programmableweb.com/category/all/apis). Найти среди них любое,
# требующее авторизацию (любого типа). Выполнить запросы к нему, пройдя авторизацию. Ответ сервера записать в файл.

import requests

user_id = 'kikoooiemama'
access_token='2821b480390f4e5cbda80e36caa90ece362a225f40d53cdc1d95823ec1bc39a533930b59d543cb9f1defc'
version = '5.131'
url = 'https://api.vk.com/method/groups.get'

params = {
    'v': version,
    'access_token': access_token
}
response = requests.get(url, params=params)

if response.ok:
    data_groups_id = response.json()
    groups_file = open('groups_vk.json', 'w', encoding="utf-8")
    groups_file.write(f'{data_groups_id}')
    groups_file.close()
    # Выведем id групп:
    print(f"Пользователь: {user_id}\n"
          f"ID Сообществ: {data_groups_id.get('response')['items']}")
else:
    print('Ошибка! Возможно некорректный токен.')
