import requests
import json
from tqdm import tqdm

VK_API_VERSION = '5.131'
YANDEX_DISK_UPLOAD_URL = 'https://cloud-api.yandex.net/v1/disk/resources/upload'


def get_vk_photos(user_id, vk_token):
    url = f'https://api.vk.com/method/photos.getAll'
    params = {
        'owner_id': user_id,
        'access_token': vk_token,
        'v': VK_API_VERSION,
        'no_service_albums': 1,
        'extended': 1
    }
    response = requests.get(url, params=params)

    if response.status_code != 200 or 'error' in response.json():
        raise Exception("Ошибка при получении фотографий: " + str(response.json()))

    return response.json()['response']['items']


def upload_photo_to_yandex(photo_url, yandex_token, folder_name, file_name):
    headers = {
        'Authorization': f'OAuth {yandex_token}'
    }

    upload_url_response = requests.post(
        YANDEX_DISK_UPLOAD_URL,
        headers=headers,
        json={"path": f"{folder_name}/{file_name}", "url": photo_url}
    )

    if upload_url_response.status_code != 201:
        raise Exception("Ошибка при загрузке фотографии на Яндекс Диск: " + str(upload_url_response.json()))

    return True


def main():
    user_id = input("Введите id пользователя VK: ")
    vk_token = input("Введите токен VK: ")
    yandex_token = input("Введите токен Яндекс.Диска: ")

    photos = get_vk_photos(user_id, vk_token)

    saved_photos_info = {}

    for photo in tqdm(photos, desc="Обработка фотографий"):
        if not photo.get('sizes'):
            continue

        max_size_photo = max(photo['sizes'], key=lambda x: x.get('width', 0) * x.get('height', 0))
        photo_url = max_size_photo['url']

        likes_count = str(photo['likes']['count'])
        date_uploaded = photo['date']

        key_name = likes_count

        if key_name in saved_photos_info:
            key_name += f"_{date_uploaded}"

        saved_photos_info[key_name] = {
            "size": f"{max_size_photo['width']}x{max_size_photo['height']}",
            "url": photo_url
        }

    for file_name, info in saved_photos_info.items():
        if upload_photo_to_yandex(info["url"], yandex_token, f'vk_photos_{user_id}', f"{file_name}.jpg"):
            print(f"Загружено: {file_name}.jpg")

    with open('saved_photos_info.json', 'w') as json_file:
        json.dump(saved_photos_info, json_file, indent=4)


if __name__ == "__main__":
    main()
