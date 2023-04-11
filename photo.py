import requests
import json
import os

def clear_derectoryia()-> None:
    """
    Очищаем папку временных фотографий
    """
    files = os.listdir('catalog_photo')
    for i in files:
        name = 'catalog_photo/' + str(i)
        os.remove(name)
def update_photo(id: str, count_photo: int)->None:
    """
    Заполняем папку временных фотографий одного отеля
    """
    count = 0
    url = "https://hotels4.p.rapidapi.com/properties/get-hotel-photos"

    querystring = {"id": id}

    headers = {
        "X-RapidAPI-Key": "991bb3cbf7msh90a6b8443de9142p1073c6jsn738effcb9067",
        "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
    }

    response = requests.request("GET", url, headers=headers, params=querystring)
    data = json.loads(response.text)
    for i in data["hotelImages"]:
        if count != count_photo:
            img = i['baseUrl'].format(size='z')
            p = requests.get(img)
            out = open(f"catalog_photo/photo_{str(count)}.jpg", "wb")
            out.write(p.content)
            out.close()
            count += 1
