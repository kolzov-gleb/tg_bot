import telebot
import api
import photo
from datetime import datetime
from telebot import types
import os
from telegram_bot_calendar import DetailedTelegramCalendar
def write_bd(text: str, message)-> None:
    """
    Заполняем файл временных данных о пользователи
    :param text: (str) получает текст с информацией вводимой пользователем
    :param message: (telebot.types.Message)
    """
    with open(f'time_bd{message.chat.id}', 'a') as file:
        file.write(text + '\n')


bot = telebot.TeleBot('5548068766:AAGRnszqHNdJqulv0Em3zvK6ECPEMjjP3gQ')
@bot.message_handler(commands=['start', 'help'])
def start_rel(message):
    """
    Отслеживание команнды помощи и
     приветсвие с возможностями бота
     Создание кнопок
    :param message: (telebot.types.Message)
    """
    murkup_menu = types.ReplyKeyboardMarkup()
    help_user = types.KeyboardButton('/help')
    lowprice = types.KeyboardButton('/lowprice')
    highprice = types.KeyboardButton('/highprice')
    history = types.KeyboardButton('/history')
    bestdeal = types.KeyboardButton('/bestdeal')
    murkup_menu.add(lowprice, highprice, bestdeal, history, help_user)
    bot.send_message(message.chat.id, "Привет. Я могу\n1. Узнать топ самых дешёвых отелей в городе (команда /lowprice).\n"
                                          "2. Узнать топ самых дорогих отелей в городе (команда /highprice).\n"
                                          "3. Узнать топ отелей, наиболее подходящих по цене и расположению от центра(самые дешёвые и находятся ближе всего к центру) (команда /bestdeal).\n"
                                          "4. Узнать историю поиска отелей (команда /history).", reply_markup=murkup_menu)
@bot.message_handler(commands=['lowprice', 'highprice', 'bestdeal'])
def search_hotel(message):
    """
    Очистка файла временных данных
    запись команды и переход к  сбору данных
    :param message: (telebot.types.Message)
    """
    with open(f'time_bd{message.chat.id}', 'w') as file:
        file.write(str(message.text) + '\n')
    collection(message)

def collection(message)->None:
    """
    Узнаем город и переход к city
    :param message: (telebot.types.Message)
    """

    send = bot.send_message(message.chat.id,'Введи город')
    bot.register_next_step_handler(send, city)

def city(message)->None:
    """
    Запись города с созданием календаря
    :param message: (telebot.types.Message)
    """
    write_bd(str(message.text), message)
    bot.send_message(message.chat.id, 'Выбери дату с какого по какое число считать стоимость гостиницы')
    calendar, step = DetailedTelegramCalendar().build()
    bot.send_message(message.chat.id, "С какого числа?", reply_markup=calendar)
    bot.send_message(message.chat.id, "До какого числа?", reply_markup=calendar)

@bot.callback_query_handler(func=DetailedTelegramCalendar.func())
def cal(c: telebot.types.CallbackQuery, data_user: list = [])->None:
    """
    Отслеживание выбора в календаре
    и запись в файл
    :param c: (telebot.types.CallbackQuery) данные календаря
    :param data_user: (list) заполняется выбором пользователя
    """
    result, key, step = DetailedTelegramCalendar().process(c.data)
    if not result and key:
        bot.edit_message_text("Выбирай", c.message.chat.id, c.message.message_id, reply_markup=key)
    elif result:
        bot.edit_message_text(f"Выбор сделан {result}", c.message.chat.id, c.message.message_id)
    if result != None:
        data_user.append(result)
    if len(data_user) == 2:
        if data_user[0] > data_user[1]:
            data_user[0], data_user[1] = data_user[1], data_user[0]
        res_data = str(data_user[0]) + ' ' + str(data_user[1])
        data(c.message)
        write_bd(res_data, c.message)
        data_user.clear()

def data (message)->None:
    """
    Узнаем сколько отелей
    :param message: (telebot.types.Message)
    """
    send = bot.send_message(message.chat.id, 'Введи кол-во отелей до 5')
    bot.register_next_step_handler(send, check_photo)

def check_photo(message)->None:
    """
    Создание инлайн клавиатуры с проверкой кол-ва отелей
    """
    if message.text.isdigit():
        if 0 < int(message.text) < 6:
            write_bd(str(message.text), message)
            kb = types.InlineKeyboardMarkup()
            markup_yes = types.InlineKeyboardButton(text='да', callback_data='yes')
            markup_no = types.InlineKeyboardButton(text = 'нет', callback_data='no')
            kb.add(markup_yes, markup_no)
            bot.send_message(message.chat.id, 'Нужны фотографии?', reply_markup=kb)
        else:
            bot.send_message(message.chat.id, 'Неправильно ввел. Заново')
            data(message)
    else:
        bot.send_message(message.chat.id, 'Нужно число. Заново')
        data(message)
@bot.callback_query_handler(func= lambda callback: callback.data)
def check_callback(callback)->None:
    """
    Отслеживание всех инлайн-клавиатур
    """
    if callback.data == 'yes':
        send = bot.send_message(callback.message.chat.id, 'Сколько фотографий, не больше 5?')
        bot.register_next_step_handler(send, photo_write)
    elif callback.data == 'no':
        write_bd('0', callback.message)
        disp(callback.message)

    elif callback.data == 'да':
        work(callback.message)
    elif callback.data == 'нет':
        with open(f'time_bd{callback.message.chat.id}', 'r') as file:
            command = file.readline()
        callback.message.text = command[:-1]
        search_hotel(callback.message)

def photo_write(message)->None:
    """
    Проверка кол-во фотографий
    """
    if message.text.isdigit():
        if 0 < int(message.text) < 6:
            write_bd(str(message.text), message)
            disp(message)
        else:
            bot.send_message(message.chat.id, 'Неправильно ввел. Заново')
            send = bot.send_message(message.chat.id, 'Сколько фотографий, не больше 5?')
            bot.register_next_step_handler(send, photo_write)
    else:
        bot.send_message(message.chat.id, 'Нужно число. Заново')
        send = bot.send_message(message.chat.id, 'Сколько фотографий, не больше 5?')
        bot.register_next_step_handler(send, photo_write)

def disp(message)->None:
    """
    Вывод собранной информации на экран
    """
    with open(f'time_bd{message.chat.id}','r') as file:
        my_list = [i[:-1] for i in file]
    help_data = my_list[2].split(' ')
    start = help_data[0]
    stop = help_data[1]
    bot.send_message(message.chat.id,
                     'Кол-во отелей:{count}\n в городе: {city}\n Кол-во фотографий {amt}\n дата с {start} по {stop} '.format(
                         count=my_list[3],
                         city=my_list[1],
                                amt=my_list[4],
                                      start=start,
                                              stop=stop
    ))
    if my_list[0] == '/bestdeal':
        bot.send_message(message.chat.id, 'Доп параметры')
        help_price(message)
    else:
        check(message)

def help_price(message)->None:
    """
     Помошник сбора доп данных
     """
    send = bot.send_message(message.chat.id, 'Диапазон цен. Формат (min-max)')
    bot.register_next_step_handler(send, price)

def price(message)->None:
    """
     Сбор доп данных для лучших отелей
    """
    buy = message.text
    buy = str(buy).split('-')
    if len(message.text) == 1:
        bot.send_message(message.chat.id, 'Ошибка. Введите цифрами согласно формату')
        help_landmarks(message)
    if buy[0].isdigit() and buy[1].isdigit():
        if int(buy[0]) > int(buy[1]):
            buy[1], buy[0] = buy[0], buy[1]
        buy = ' '.join(buy)
        write_bd(str(buy), message)
        help_landmarks(message)
    else:
        bot.send_message(message.chat.id, 'Ошибка. Введите цифрами согласно формату')
        help_price(message)


def help_landmarks(message)->None:
    """
    Помошник сбора доп данных
    """
    send = bot.send_message(message.chat.id, 'Диапозон расстояние до цента. Формат (min-max)')
    bot.register_next_step_handler(send, landmarks)

def landmarks(message)->None:
    """
    Сбор доп данных для лучших отелей
    """
    line = message.text
    line = str(line).split('-')
    if len(message.text) == 1:
        bot.send_message(message.chat.id, 'Ошибка. Введите цифрами согласно формату')
        help_landmarks(message)
    if line[0].isdigit() and line[1].isdigit():
        if int(line[0]) > int(line[1]):
            line[1], line[0] = line[0], line[1]
        line = ' '.join(line)
        write_bd(str(line), message)
        check(message)
    else:
        bot.send_message(message.chat.id, 'Ошибка. Введите цифрами согласно формату')
        help_landmarks(message)
def check(message)->None:
    """
    Инлайн клавиатура да или нет
    """
    kb = types.InlineKeyboardMarkup()
    markup_yes = types.InlineKeyboardButton(text='да', callback_data='да')
    markup_no = types.InlineKeyboardButton(text='нет', callback_data='нет')
    kb.add(markup_yes, markup_no)
    bot.send_message(message.chat.id, 'Верно?', reply_markup=kb)

def work(message)->None:
    """
    Основная функция сбора данных по критериям юзера
    """
    with open(f'time_bd{message.chat.id}','r') as file:
        my_list = [i[:-1] for i in file]
    bot.send_message(message.chat.id, 'Работаем')
    help_data = my_list[2].split(' ')
    start = help_data[0]
    stop = help_data[1]
    try:
        my_list_hotels = api.search(city=my_list[1], checkin=start, checkout=stop)
        if my_list_hotels == False:
            bot.send_message(message.chat.id, 'Ошибка с данными. Проверьти достоверность информации и выберите заного команду. Помните, что город нужно вводить на английском')
            start_rel(message)
        else:
            with open(f'bd/{message.chat.id}', 'a') as file:
                wr = my_list[0] + ' - ' + str(datetime.today()) + ' - '
                file.write(wr)
            if my_list[0] == '/lowprice':
                bot.send_message(message.chat.id, 'Дешевые')
                my_list_hotels.sort(key=lambda my_list_hotels: my_list_hotels[4])
                res_disp(my_list_hotels, my_list, message)
            elif my_list[0] == '/highprice':
                bot.send_message(message.chat.id, 'Дороги')
                my_list_hotels.sort(key=lambda my_list_hotels: my_list_hotels[4])
                my_list_hotels.reverse()
                res_disp(my_list_hotels, my_list, message)
            elif my_list[0] == '/bestdeal':
                bot.send_message(message.chat.id, 'Лучшие')
                help_price = my_list[5].split(' ')
                min_price = int(help_price[0])
                max_price = int(help_price[1])
                help_landmark = my_list[6].split(' ')
                min_land = int(help_landmark[0])
                max_land = int(help_landmark[1])
                print('поиск')
                my_list_hotels.sort(key=lambda my_list_hotels: my_list_hotels[4])
                res = list(filter(lambda my_list_hotels: min_price <= int(my_list_hotels[4]) <= max_price, my_list_hotels))
                my_list_hotels = list(filter(lambda res: min_land <= float(res[3][:res[3].find(' ')]) <= max_land, res))
                if len(my_list_hotels) == 0:
                    bot.send_message(message.chat.id, 'Отелей удовлетворяющих требования нету')
                    start_rel(message)
                res_disp(my_list_hotels, my_list, message)
    except KeyError:
        bot.send_message(message.chat.id, 'Ошибка. Извините,но заново')
        start_rel(message)



def res_disp(my_list_hotels: list, my_list: list, message: telebot.types.Message):
    """
    Отправка пользавателю результатов
    :param my_list_hotels: (list) список всех отелей
    :param my_list: (list) список с информацией от пользователя
    """
    count = 0
    chek_count_photo = 0
    memory = ''
    for i in my_list_hotels:
        if i[1] != memory:
            if count != int(my_list[3]):
                count += 1
                memory = i[1]
                adress = ' '.join(i[2])
                disp = f'Название отеля {i[1]},\nадрес {adress},\nкак далеко расположен от центра {i[3]},' \
                   f'\nцена за ночь {i[4]},\nцена за все время {i[5]}\n https://www.hotels.com/ho{i[0]}'
                bot.send_message(message.chat.id, disp)
                with open(f'bd/{message.chat.id}', 'a') as file:
                    wr = str(i[1]) + ', '
                    file.write(wr)
                user_photo = 'Фото'.format(my_list[4])
                bot.send_message(message.chat.id, user_photo)
                if int(my_list[4]) == 0:
                    bot.send_message(message.chat.id,'Не требуется')
                else:
                    amt = 0
                    photo.clear_derectoryia()
                    photo.update_photo(f"{str(my_list_hotels[chek_count_photo][0])}", int(my_list[4]))
                    for i in range(int(my_list[4])):
                        user_photo = open(f"catalog_photo/photo_{str(amt)}.jpg", 'rb')
                        bot.send_photo(message.chat.id, user_photo)
                        amt += 1
        chek_count_photo += 1
    with open(f'bd/{message.chat.id}', 'a') as file:
        file.write('\n')

@bot.message_handler(commands=['history'])
def history(message):
    """
    Заполненние базы данных
    """
    file = os.listdir('bd')
    if str(message.chat.id) in file:
        with open(f'bd/{message.chat.id}', 'r') as user:
            for i in user:
                disp = str(i)
                print(disp)
                if i != '\n':
                    bot.send_message(message.chat.id, disp)
    else:
        bot.send_message(message.chat.id, 'Информации нету')


bot.polling(none_stop=True, interval=0)