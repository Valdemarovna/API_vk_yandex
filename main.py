# id приложения 51893580
# id пользователя 839999473
# яндекс токен 'ваш я_токен'
import requests

class VK:
    def __init__(self, access_token, user_id, version='5.131'):
        self.token = access_token
        self.id = user_id
        self.version = version
        self.params = {'access_token': self.token, 'v': self.version}

    def get_profile_photo(self):
        url = 'https://api.vk.com/method/photos.get'
        params = {'user_ids': self.id, 'album_id': 'profile', 'extended': 1}
        response = requests.get(url, params={**self.params, **params})
        return response.json()

access_token = 'ваш access token vk'
user_id = input('Введите ID пользователя: ')
# user_id = '839999473'
vk = VK(access_token, user_id)
photo_info = vk.get_profile_photo()

print(f"В данном профиле {len(photo_info['response']['items'])} фото")

count_to_dl = input('Введите кол-во фото для загрузки(не более 5 фото): ')
if int(count_to_dl) > 5:
    print('НЕ БОЛЕЕ 5!!!')
    exit(1)
photo_dict = {}
for i in photo_info['response']['items']:
    counter = 0
    photo_dict.setdefault(i['id'], {'likes_count': i['likes']['count'], 'photo_url': i['sizes'][-1]['url']})
    counter +=1
    if counter == 5 or counter == int(count_to_dl):
        break

for k,v in photo_dict.items():

    # Скачиваем файл на компьютер
    response = requests.get(v['photo_url'])
    if 200 <= response.status_code < 300:
        with open(f'{v["likes_count"]}.jpg', 'wb') as file:
            file.write(response.content)
        print(f'Файл {v["likes_count"]}.jpg скачен.')

    # Создаем папку Image на яд
    params = {'path': 'Image'}
    headers = {'Authorization': 'OAuth здесь_ваш_токен'}
    response = requests.put('https://cloud-api.yandex.net/v1/disk/resources',
                            headers=headers,
                            params=params)
    if 200 <= response.status_code < 300:
        print('Папка создана.')
    else:
        print('Папка НЕ создана или уже существует.')


    # Запрашивает URL у яд для загрузки
    url = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
    params = {'path': f'Image/{v["likes_count"]}.jpg'}
    headers = {'Authorization': 'OAuth здесь_ваш_токен'}
    response = requests.get(url,
                            params=params,
                            headers=headers)
    url_for_upload = response.json().get('href', '')
    if 200 <= response.status_code < 300:
        print('Ссылка для сохранения файла на яндекс диск получена.')
    else:
        print('Ссылка для сохранения файла на яндекс диск НЕ получена.')
        continue

    # Загружает на диск файлы по полученному URL
    with open(f'{v["likes_count"]}.jpg', 'rb') as file:
        response = requests.put(url_for_upload, files={"file": file})

    if 200 <= response.status_code < 300:
        print(f'Файл {v["likes_count"]}.jpg сохранен на Яндекс диске.')
    else:
        print(f'Файл {v["likes_count"]}.jpg не сохранен на Яндекс диске.')