import requests
import configparser
from datetime import datetime
import json


def main():
    class VK:
        def __init__(self, access_token, user_id):
            self.token = access_token
            self.id = user_id

        def get_profile_photo(self, count=5):
            url = 'https://api.vk.com/method/photos.get'
            params = {'access_token': self.token,
                      'owner_id': self.id,
                      'album_id': 'profile',
                      'extended': 1,
                      'v': '5.131',
                      'photo_sizes': '1',
                      'count': count
                      }
            response = requests.get(url, params=params)
            photo_amount = len(response.json()['response']['items'])
            print(f'По данному профилю получено {photo_amount} фотографий')
            return response.json()

        def get_final_json(self):
            photo_info = vk.get_profile_photo()
            photo_dict = {}
            for i in photo_info['response']['items']:
                right_date = datetime.fromtimestamp(i['date'])
                for j in i['sizes']:
                    if j['type'] == 'z':
                        url_max_size =j['url']
                if str(i['likes']['count']) in photo_dict.keys():
                    photo_dict.setdefault(str(i['likes']['count']) + "-" + str(right_date.strftime('%Y-%m-%d')),
                                          [url_max_size, 'z'])
                else:
                    photo_dict.setdefault(str(i['likes']['count']), [url_max_size, 'z'])
            return photo_dict

    class yandex:
        def __init__(self, y_token):
            self.token = y_token

        def create_dir(self, dir_name):
            params = {'path': dir_name,
                      'overwrite': 'false'}
            headers = {'Authorization': self.token}
            response = requests.put('https://cloud-api.yandex.net/v1/disk/resources',
                                    headers=headers,
                                    params=params)
            if 200 <= response.status_code < 300:
                print(f'Папка {dir_name} на Яндекс диске создана.')
                return response.json()
            else:
                print(f'Папка {dir_name} НЕ создана или уже существует.')

        def get_upload_url(self, file_name, dir_name):
            url = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
            params = {'path': f'{dir_name}/{file_name}.jpg', 'overwrite': 'true'}
            headers = {'Authorization': self.token}
            response = requests.get(url,
                                    params=params,
                                    headers=headers)
            url_for_upload = response.json().get('href', '')
            if 200 <= response.status_code < 300:
                print(f'Ссылка для сохранения файла {file_name}.jpg на яндекс диск получена.')
                return url_for_upload
            else:
                print(f'Ссылка для сохранения файла {file_name}.jpg на яндекс диск НЕ получена.')

        def upload_photo(self, url_upload, file_url):
            resp = requests.get(file_url)
            response = requests.put(url_upload, data=resp.content)
            if 200 <= response.status_code < 300:
                print(f'Файл загружен на яндекс диск.')
            else:
                print(f'Файл Не загружен на яндекс диск.')
            # return response.json

    # Достаем ключи из конфигурации файла
    config = configparser.ConfigParser()
    config.read("tokens.ini")
    access_token = config["info"]["vk"]
    ytoken = config["info"]["ya"]

    # Получаем ID пользователя
    user_id = input('Введите ID пользователя: ')
    vk = VK(access_token, user_id)

    # Получаем фотографии пользователя
    photo_info = vk.get_final_json()

    # Создаем папку на яндекс диске
    ya = yandex(ytoken)
    ya.create_dir('photo')

    # Загружаем фотогрфии на яндекс диск
    output_json = []
    for k, v in photo_info.items():
        upload_url = ya.get_upload_url(k, 'photo')
        uploaded = ya.upload_photo(upload_url, v[0])
        output_json.append({"File name": k,
                            "size": v[1]})
    with open("photos.json", "w") as file:
        json.dump(output_json, file, indent=4)
    print(f'\nПрограмма выполнена, фотографии пользователя ID - {user_id}, успешно сохранены на Яндекс диске!')

if __name__ == '__main__':
    main()