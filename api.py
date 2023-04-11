import requests
import json
my_list_hotel = []

def search(city: str, checkin: str, checkout: str):
    """
    Собираем информацию об отели
    :param city:(str) город пользователя
    :param checkin:(str) дата заезда
    :param checkout:(str) лвата выезда
    :return: (list) список отелей либо False
    """
    url = "https://hotels4.p.rapidapi.com/locations/v2/search"
    querystring = {"query": f"{city}"}
    headers = {"X-RapidAPI-Key": "991bb3cbf7msh90a6b8443de9142p1073c6jsn738effcb9067",
               "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
               }
    response = requests.request("GET", url, headers=headers, params=querystring)
    data = json.loads(response.text)
    if len(data) == 0:
        return False
    elif data['moresuggestions'] == 0:
        return False
    for i in data['suggestions'][0]['entities']:
        url = "https://hotels4.p.rapidapi.com/properties/list"
        querystring = {"destinationId":f"{i['destinationId']}","pageNumber":"1","pageSize":"25","checkIn":f"{checkin}","checkOut":f"{checkout}","adults1":"1","sortOrder":"PRICE"}
        headers = {
                "X-RapidAPI-Key": "991bb3cbf7msh90a6b8443de9142p1073c6jsn738effcb9067",
                "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
            }
        response = requests.request("GET", url, headers=headers, params=querystring)
        data = json.loads(response.text)
        if not('data' in data):
            return False
        for i in data['data']['body']['searchResults']['results']:
            if "fullyBundledPricePerStay" in i["ratePlan"]["price"]:
                if "streetAddress" in i["address"]:
                    my_list_hotel.append([i['id'], i['name'],
                                              [i["address"]["locality"], i["address"]["streetAddress"]],
                                              i["landmarks"][0]["distance"],
                                              i["ratePlan"]["price"]["exactCurrent"],
                                              i["ratePlan"]["price"]["fullyBundledPricePerStay"]])
                else:
                    my_list_hotel.append([i['id'], i['name'],
                                              [i["address"]["locality"]],
                                              i["landmarks"][0]["distance"],
                                              i["ratePlan"]["price"]["exactCurrent"],
                                              i["ratePlan"]["price"]["fullyBundledPricePerStay"]])
            else:
                if "streetAddress" in i["address"]:
                    my_list_hotel.append([i['id'],i['name'],
                                              [i["address"]["locality"], i["address"]["streetAddress"]],
                                              i["landmarks"][0]["distance"],
                                              i["ratePlan"]["price"]["exactCurrent"],
                                              'неизвестно'])
                else:
                    my_list_hotel.append([i['id'], i['name'],
                                              [i["address"]["locality"]],
                                              i["landmarks"][0]["distance"],
                                              i["ratePlan"]["price"]["exactCurrent"],
                                              'неизвестно'])

    return (my_list_hotel)




