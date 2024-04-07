from telebot import types # для указание типов

limit_text_len = 3000

INTERVIEW_BLANK = ['Вопрос 1:Кикие точки роста для персонала вы видите?','Ответ:None.',
                   'Вопрос 2:Зачем?','Ответ:None.',
                   'Вопрос 3:Почему?','Ответ:None.',
                   'Вопрос 4:Откуда?','Ответ:None.',
                   'Вопрос 5:Как?','Ответ:None.',]

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
