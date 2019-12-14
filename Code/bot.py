import telebot
import Parse
from datetime import datetime
from pymorphy2 import MorphAnalyzer
import locale

API_KEY = '' #ЗДЕСЬ НУЖЕН API TELEGRAM БОТА
bot = telebot.TeleBot(API_KEY)

start_buttons = ['🗓 Важные судебные заседания в ближайшее время', '🏣 Найти адрес суда']
case_buttons = ['Все дела', 'На завтра', 'На послезавтра', 'На другой день', 'На главную']
back_button = ['На главную']

def check_cases_by_date(date):
    if type(date) == float:
        date = datetime.fromtimestamp(date)
    date = date.replace(year=1900,hour=0,minute=0,second=0,microsecond = 0)
    morph = MorphAnalyzer()
    all_cases = Parse.main()
    actual_cases = []
    for i in range(len(all_cases)):
        time = all_cases[i]['time']
        time = ' '.join([time.split(' ')[0], morph.parse(time.split(' ')[1])[0].inflect({'nomn'}).word])
        if datetime.strptime(time, '%d %B') == date:
            actual_cases.append(all_cases[i])
    return actual_cases

def get_keyboard(message, buttons):
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard = True)
    keyboard.add(*[telebot.types.KeyboardButton(name) for name in buttons])
    return keyboard

def find_in_array(place, array):
    for i in range(len(array)):
        if array[i]['name'] == place:
            return [True, i]
    return [False, -1]

@bot.message_handler(commands=['start'])
def start(message):
    keyboard = get_keyboard(message, start_buttons)
    bot.send_message(message.from_user.id, '''Привет!
Вы можете посмотреть список важнейших судебных заседаний по мнению Медиазоны в удобную вам дату или найти адрес нужного суда.''', reply_markup = keyboard)
@bot.message_handler(content_types=['text'])
def main(message):
    locale.setlocale(locale.LC_ALL, 'ru')
    if message.text == start_buttons[0]:
        keyboard = get_keyboard(message, case_buttons)
        bot.send_message(message.from_user.id, 'На какой день вам интересно?', reply_markup = keyboard)
    if message.text == case_buttons[0]:
        cases = Parse.make_htmls(Parse.main())
        for i in range(len(cases)):
            bot.send_message(message.from_user.id, cases[i], parse_mode = 'HTML', reply_markup = get_keyboard(message, back_button))
    if message.text == back_button[0]:
        keyboard = get_keyboard(message, start_buttons)
        bot.send_message(message.from_user.id, '''Привет!
Вы можете посмотреть список важнейших судебных заседаний по мнению Медиазоны в удобную вам дату или найти адрес нужного суда.''', reply_markup = keyboard)
    if message.text == case_buttons[1]:
        cases = check_cases_by_date(datetime.timestamp(datetime.now()) + 86400)
        if len(cases) == 0:
            bot.send_message(message.from_user.id, "На данный день судов не найдено. Попробуйте в другой раз.", reply_markup = get_keyboard(message, back_button))
        else:
            html_cases = Parse.make_htmls(cases)
            for i in range(len(html_cases)):
                bot.send_message(message.from_user.id, html_cases[i], parse_mode = "HTML", reply_markup = get_keyboard(message, back_button))
    if message.text == case_buttons[2]:
        cases = check_cases_by_date(datetime.timestamp(datetime.now()) + 172800)
        if len(cases) == 0:
            bot.send_message(message.from_user.id, "На данный день судов не найдено. Попробуйте в другой раз.", reply_markup = get_keyboard(message, back_button))
        else:
            html_cases = Parse.make_htmls(cases)
            for i in range(len(html_cases)):
                bot.send_message(message.from_user.id, html_cases[i], parse_mode = "HTML", reply_markup = get_keyboard(message, back_button))
    if message.text == case_buttons[3]:
        mes = bot.send_message(message.from_user.id,'Отправьте дату в формате: DD.MM', reply_markup = get_keyboard(message, back_button))
        bot.register_next_step_handler(mes, get_date)
    if message.text == start_buttons[1]:
        justice_buttons = []
        justice = []
        cases = Parse.main()
        for i in range(len(cases)):
            index = find_in_array(cases[i]['place'], justice)
            if not(index[0]):
                justice.append({'name':cases[i]['place'],'count': 1})
            else:
                justice[index[1]]['count'] += 1
        for i in range(len(justice) - 1):
            for j in range(len(justice) - 1):
                if justice[j]['count'] < justice[j+1]['count']:
                    justice[j], justice[j+1] = justice[j+1], justice[j]
        for i in range(4):
            justice_buttons.append(justice[i]['name'])
        justice_buttons.append('На главную')
        mes = bot.send_message(message.from_user.id, 'Выберите из предложенных судов или введите вручную.', reply_markup = get_keyboard(message,justice_buttons))
        bot.register_next_step_handler(mes, get_address)

def get_address(message):
    if message.text == back_button[0]:
        keyboard = get_keyboard(message, start_buttons)
        bot.send_message(message.from_user.id, '''Привет!
Вы можете посмотреть список важнейших судебных заседаний по мнению Медиазоны в удобную вам дату или найти адрес нужного суда.''', reply_markup = keyboard)
    location = Parse.get_coordinates(message.text)
    bot.send_location(message.from_user.id, longitude=location[0], latitude = location[1], reply_markup = get_keyboard(message, back_button))

def get_date(message):
    if message.text == back_button[0]:
        keyboard = get_keyboard(message, start_buttons)
        bot.send_message(message.from_user.id, '''Привет!
Вы можете посмотреть список важнейших судебных заседаний по мнению Медиазоны в удобную вам дату или найти адрес нужного суда.''', reply_markup = keyboard)
    if (len(message.text.split('.')) == 2) and (0 < int(message.text.split('.')[0]) <= 31) and (0 < int(message.text.split('.')[1]) <= 12):
        date = datetime.strptime(message.text, '%d.%m')
        cases = check_cases_by_date(date)
        if len(cases) == 0:
            bot.send_message(message.from_user.id, "На данный день судов не найдено. Попробуйте в другой раз.", reply_markup = get_keyboard(message, back_button))
        html_cases = Parse.make_htmls(cases)
        for i in range(len(html_cases)):
            bot.send_message(message.from_user.id, html_cases[i], parse_mode = "HTML", reply_markup = get_keyboard(message, back_button))
    else:
        mes = bot.send_message(message.from_user.id, 'Неверный формат даты. Отправьте дату в формате: DD.MM', reply_markup = get_keyboard(message, back_button))
        bot.register_next_step_handler(mes, get_date)
bot.polling(none_stop=True, interval=0)
