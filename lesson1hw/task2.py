# Задание №2. Изучить список открытых API (https://www.programmableweb.com/category/all/apis). Найти среди них любое,
# требующее авторизацию (любого типа). Выполнить запросы к нему, пройдя авторизацию. Ответ сервера записать в файл.

import requests

user_id = 'kikoooiemama'
access_token='token'
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
