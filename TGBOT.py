import telebot
from telebot import types
import sqlite3
import requests
import os
import collections
collections.Callable = collections.abc.Callable
Callable = collections.Callable
import numpy as np
import matplotlib.pyplot as plt
import datetime

url_auth = "https://sh-open.ris61edu.ru/auth/login"
url = "https://sh-open.ris61edu.ru/personal-area/#marks"

now = datetime.datetime.now()
a = str(now.year), '-', str(now.month),'-',str(now.day)
DATE = ''
for i in a:
    DATE += i
url_grades = f'https://sh-open.ris61edu.ru/api/MarkService/GetSummaryMarks?date={DATE}'


bot = telebot.TeleBot('6934522253:AAHQEyGcD8_ebYmIW-z-2J04D7zwkuVZ-jI')



@bot.message_handler(commands=['start'])
def main(message):
    global b1
    global user_id
    user_id = message.from_user.id
    conn = sqlite3.connect('ocr_lip.sql')
    cur = conn.cursor()

    cur.execute(
        'CREATE TABLE IF NOT EXISTS users '
        
        '(id int auto_increment primary key, '
        'tg_id varchar(50),'
        'name varchar(50), '
        'class varchar(50), '
        'graph_photo BLOB, '
        'login_for_bars varchar(50), '
        'pass_for_bars varchar(50) )')

    conn.commit()
    cur.close()
    conn.close

    markup2 = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton('', callback_data='register')
    btn2 = types.InlineKeyboardButton('Мои аккаунты', callback_data='my_accounts')
    btn3 = types.InlineKeyboardButton('Оценки', callback_data='grades')

    markup2.row(btn2,btn3)
    markup2.row(btn1)


    a = bot.send_message(message.chat.id, f'🎒 Приветствуем вас в электронном дневнике с оценками! Здесь вы сможете увидеть свои оценки, а также следить за своим прогрессом в учебе. 🏅 Не забудьте проверять свой дневник каждый день, чтобы быть в курсе своих успехов.', reply_markup=markup2)
    b1 = a.message_id

@bot.callback_query_handler(func=lambda callback: True)
def callback_message(callback):
    global b1
    global disciplines
    global user_id
    global FOR_GRAPH


    if callback.data == 'my_accounts':
        conn = sqlite3.connect('ocr_lip.sql')
        cur = conn.cursor()

        cur.execute('SELECT * FROM users WHERE tg_id = ?', [user_id])
        basas = cur.fetchall()
        info = ''
        for el in basas:
            info += f'Имя: {el[2]}. Класс : {el[3]}.\nЛогин от "БАРС": {el[5]} Пароль: {el[6]}.\n'
        cur.close()
        conn.close()

        markup2 = types.InlineKeyboardMarkup()
        # btn1 = types.InlineKeyboardButton('Войти в аккаунт', callback_data='join')
        btn2 = types.InlineKeyboardButton('Добавить новый аккаунт', callback_data='register')
        btn3 = types.InlineKeyboardButton('Удалить аккаунт', callback_data='delete_account')

        markup2.row(btn2, btn3)
        try:
            bot.send_message(callback.message.chat.id, info, reply_markup=markup2)
        except:
            bot.send_message(callback.message.chat.id, 'Введите имя и фамилию для регистрации')
            bot.register_next_step_handler(callback.message, user_name)

    elif callback.data == 'grades':

        bot.send_message(callback.message.chat.id, f'Вот ваши оценки. Это может занять некоторое время.')
        google_sheet_grades(callback.message)


    elif callback.data == 'delete_account':
        bot.send_message(callback.message.chat.id, 'Введите имя аккаунта для удаления')
        bot.register_next_step_handler(callback.message, delete_account)

    elif callback.data == 'register':
        bot.send_message(callback.message.chat.id, 'Введите имя и фамилию')
        bot.register_next_step_handler(callback.message, user_name)

    elif callback.data == 'graph_select':

        markup2 = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton(f'{disciplines[0]}', callback_data=f'{disciplines[0]}')
        btn2 = types.InlineKeyboardButton(f'{disciplines[1]}', callback_data=f'{disciplines[1]}')
        btn3 = types.InlineKeyboardButton(f'{disciplines[2]}', callback_data=f'{disciplines[2]}')
        btn4 = types.InlineKeyboardButton(f'{disciplines[3]}', callback_data=f'{disciplines[3]}')
        btn5 = types.InlineKeyboardButton(f'{disciplines[4]}', callback_data=f'{disciplines[4]}')
        try:
            btn6 = types.InlineKeyboardButton(f'{disciplines[5]}', callback_data=f'{disciplines[5]}')
        except:
            pass
        try:
            btn7 = types.InlineKeyboardButton(f'{disciplines[6]}', callback_data=f'{disciplines[6]}')
        except:
            pass
        try:
            btn8 = types.InlineKeyboardButton(f'{disciplines[7]}', callback_data=f'{disciplines[7]}')
        except:
            pass
        try:
            btn9 = types.InlineKeyboardButton(f'{disciplines[8]}', callback_data=f'{disciplines[8]}')
        except:
            pass
        markup2.add(btn1,btn2,btn3,btn4,btn5)
        try:
            markup2.add(btn6)
        except:
            pass
        try:
            markup2.add(btn7)
        except:
            pass
        try:
            markup2.add(btn8)
        except:
            pass
        try:
            markup2.add(btn9)
        except:
            pass
        bot.send_message(callback.message.chat.id, 'Выберите предмет по которому будет построен график',reply_markup=markup2)





    elif callback.data in disciplines:
        FOR_GRAPH = callback.data
        graph(callback.message)

    elif callback.data == 'join':
        bot.send_message(callback.message.chat.id, 'Введите имя и фамилию')
        bot.register_next_step_handler(callback.message, authorize_name)









def user_name(message):
    global name
    name = message.text.strip()
    bot.send_message(message.chat.id, 'Введите класс')
    bot.register_next_step_handler(message, user_clas)




def user_clas(message):
    global clas
    clas = message.text.strip()
    bot.send_message(message.chat.id, 'Введите логин от БАРС.Образование')
    bot.register_next_step_handler(message, login_for_bars)

def login_for_bars(message):
    global login_for_diary
    login_for_diary = message.text.strip()
    bot.send_message(message.chat.id, 'Введите пароль от БАРС.Образование')
    bot.register_next_step_handler(message, user_pass)

def user_pass(message):
    user_id = message.from_user.id
    pasword_for_diary = message.text.strip()

    conn = sqlite3.connect('ocr_lip.sql')
    cur = conn.cursor()

    cur.execute("INSERT INTO users(tg_id,name, class, login_for_bars, pass_for_bars) VALUES ('%s','%s', '%s', '%s', '%s')" % (user_id,name,clas, login_for_diary, pasword_for_diary))
    conn.commit()
    cur.close()
    conn.close()

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Список ваших пользователей', callback_data='my_accounts'))
    bot.send_message(message.chat.id, 'Вы зарегестрированы!', reply_markup=markup)


def authorize_name(message):
    global secret_password
    name_for_authorize = message.text.strip()

    conn = sqlite3.connect('ocr_lip.sql')
    cur = conn.cursor()

    cur.execute('SELECT * FROM users')
    basas = cur.fetchall()
    secret_password = ''
    for el in basas:
        if el[2] == name_for_authorize:
            secret_password = ''
            secret_password += el[4]
    cur.close()
    conn.close()


    bot.send_message(message.chat.id, 'Теперь введите пароль.')
    bot.register_next_step_handler(message, authorize_password)


def authorize_password(message):
    global secret_password
    global user_id
    password_for_authorize = message.text.strip()
    if password_for_authorize == secret_password:
        bot.send_message(message.chat.id, 'Вход успешен')
    else:
        bot.send_message(message.chat.id, 'Съебал')


def delete_account(message):
    name_for_delete = message.text.strip()
    try:
        conn = sqlite3.connect('ocr_lip.sql')
        cur = conn.cursor()
        cur.execute("DELETE FROM users WHERE name = ?", (str(name_for_delete), ))
        conn.commit()
        cur.close()
        conn.close()
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('Вернуться к списку аккаунтов', callback_data='my_accounts'))
        bot.send_message(message.chat.id, f"Аккаунт успешно удалён!", reply_markup=markup)
    except:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('Вернуться к списку аккаунтов', callback_data='my_accounts'))
        bot.send_message(message.chat.id, f"Аккаунт с именем '{name_for_delete}' не обнаружен!", reply_markup=markup)
        if message.text.strip() != name_for_delete:
            delete_account(message)
        exit()





def google_sheet_grades(message):
    global user_id
    global url
    global url_grades
    global url_auth
    global disciplines
    global discipline_for_graph
    global date_for_graph


    conn = sqlite3.connect('ocr_lip.sql')
    cur = conn.cursor()

    cur.execute('SELECT * FROM users WHERE tg_id = ?', [user_id])
    basas = cur.fetchall()
    for el in basas:
        login_for_bars = el[5]
        password = el[6]


    data = {
        "login_login": str(login_for_bars),
        "login_password": str(password)
    }
    cur.close()
    conn.close()

    with requests.Session() as session:
        session.post(url_auth, data=data)
        response = session.get(url).text
        response_for_marks = session.get(url_grades)

    marks = response_for_marks.text.encode().decode('unicode-escape')
    marks = eval(marks)
    Finally_Grades = ''
    disciplines = []
    a = ''
    discipline_for_graph = {}
    date_for_graph = {}
    y = []
    p = []
    for i in marks["discipline_marks"]:
        Finally_Grades += (i['discipline'])
        disciplines.append(i['discipline'])
        name_of_discipline = i['discipline']
        Finally_Grades += '\n'
        for i in i["marks"]:
            a += f"{(i['mark'])} "
            y.append(i['mark'])
            x = (i['date'])
            b = ''
            b += b.join(x[-2])
            b += b.join(x[-1])
            b += b.join('.')
            b += b.join(x[5])
            b += b.join(x[6])
            a += b
            p.append(b)

            Finally_Grades += (a)
            Finally_Grades += '\n'
            a = ''
        discipline_for_graph[name_of_discipline] = y
        date_for_graph[name_of_discipline] = p
        y = []
        p = []
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Составить график успеваемости', callback_data='graph_select'))
    bot.send_message(message.chat.id, Finally_Grades, reply_markup=markup)



def graph(message):
    global user_id
    global discipline_for_graph
    global FOR_GRAPH
    global date_for_graph

    FOR_GRAPH = str(FOR_GRAPH)
    GRADES = discipline_for_graph[FOR_GRAPH]
    date = date_for_graph[FOR_GRAPH]

    GRADES_FOR_GRAPH = np.array(GRADES)
    DATA_DLYA_GRAPHA = np.array(date)

    RAZMETKA = ['н',2,3,4,5]
    plt.figure()
    nyli = []
    for i in date:
        nyli.append(0)
    plt.plot(RAZMETKA, color = 'white')
    plt.plot(date,nyli, color='white')

    plt.plot(GRADES)
    plt.xlabel('Дата')
    plt.ylabel('Оценка')
    title_for_graph = f'График по предмету {FOR_GRAPH}'
    plt.title(title_for_graph)
    plt.grid(True)

    plt.savefig(f'{title_for_graph}.png')
    filepath = fr'График по предмету {FOR_GRAPH}.png'
    bot.send_photo(message.chat.id, open(filepath, 'rb'), caption=f'График по предмету {FOR_GRAPH}')
    os.remove(filepath)

bot.polling(none_stop=True, interval=0)



