from telebot import types # для указание типов

limit_text_len = 3000
TOKEN = '6605355751:AAFVG5CGrn2DBMHQZG7gLodTAshtYlk-5yw'

interview_columns = ['quest1','quest2','quest3','quest4','quest5',
               'extraquest1','extraquest2','extraquest3','extraquest4','extraquest5',
               'ans1','ans2','ans3','ans4','ans5',
               'extrans1','extrans2','extrans3','extrans4','extrans5']

START_JSON_INTERVIEW = {'Client':{'О1':'','О2':'','О3':'','О4':'','О5':'','Д1':'','Д2':'','Д3':'','Д4':'','Д5':''},
                        'AI':{'О1':'','О2':'','О3':'','О4':'','О5':'','Д1':'','Д2':'','Д3':'','Д4':'','Д5':''},
                        'Deleted':False}

CLIENT_JSON_CONFIG = {'Queries':{0:0}, 'Active query':0, 'State':{'Interviewer': False, 'Helper': False,'Chat': False, 'estimator': False},'Blacklist':False}

keyboard_hi = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=False, one_time_keyboard=True)
key = types.KeyboardButton(text='Начать новое интервью.')
keyboard_hi.add(key)
key = types.KeyboardButton(text='Выбрать одно из прошлых интервью.')
keyboard_hi.add(key)

keyboard_admin = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=False, one_time_keyboard=True)
key = types.KeyboardButton(text='Начать новое интервью.')
keyboard_admin.add(key)
key = types.KeyboardButton(text='Выбрать одно из прошлых интервью.')
keyboard_admin.add(key)
key = types.KeyboardButton(text='Назначить новое интервью.')
keyboard_admin.add(key)
# MAIN_URL = f'https://api.telegram.org/bot{TOKEN}'
# URL = f'{MAIN_URL}/getMe'