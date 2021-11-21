# Задание №1. Посмотреть документацию к API GitHub, разобраться как вывести список репозиториев для конкретного
# пользователя, сохранить JSON-вывод в файле *.json.
import json
import requests

host = 'https://api.github.com'
username = 'kikoooiemama'
url = f'{host}/users/{username}/repos'
response = requests.get(url).json()
with open('repos.json', 'w') as outfile:
    json.dump(response, outfile, indent=4)
# дамп сделан, парсим названия:
print(f"Публичные репозитории пользователя '{username}':")
for repo in response:
    print(f"\t{repo['name']}")
