from telebot import types # для указание типов

limit_text_len = 3000
BIG_PARAGRAPH_THRESHOLD = 1400
SMALL_PARAGRAPH_THRESHOLD = 900
BAN_APOLOGISE = "Извините, вы были заблокированы за нарушение правил.\nДля разблокировки вам необходимо написать: Вернуться"
TOKEN_TRY_AGAIN = "Вы ввели недействитеьный токен или у вас больше одного активного интервью. Попробуйте ещё раз..."
AI_STATE_INTERVIEWER = 'AI State: Interviewer\nВсе ваши ответы кроме комманд /<...> будут рассматриваться как ответы на вопросы'
AI_STATE_ASSISTANT = 'AI State: Assistant\nВсе ваши ответы кроме комманд /<...> будут рассматриваться как навигация по меню выбора'
AI_STATE_CHAT = 'AI State: Chat\nВсе ваши ответы кроме комманд /<...> будут рассматриваться как вопросы для GPT'
USER_NOT_FOUNDED = "Ошибка.\nУбедитесь, что пользователь с таким именем зарегестрирован, проверьте правильность написания имени и попробуйте ещё раз."
NEW_USER_UNKNOWN_INPUT = 'Добро пожаловать!\nВведите /start, чтобы мы зарегистрировали вас и рассказали о возможностях нашего сервиса.'
TEXT_LEN_LIMIT_ERROR = 'Вы написали слишком большое сообщение. Это бы вызвало критическую ошибку в работе бота.'
INTERVIEW_BLANK = ['Вопрос 1:Какие точки роста для персонала вы видите?','Ответ:None.',
                   'Вопрос 2:Зачем?','Ответ:None.',
                   'Вопрос 3:Почему?','Ответ:None.',
                   'Вопрос 4:Откуда?','Ответ:None.',
                   'Вопрос 5:Как?','Ответ:None.',]

keyboard_chairs = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=False, one_time_keyboard=True)

keyboard_hi = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=False, one_time_keyboard=True)
key = types.KeyboardButton(text='Начать новое интервью.')
keyboard_hi.add(key)
key = types.KeyboardButton(text='Выбрать одно из прошлых интервью.')
keyboard_hi.add(key)
key = types.KeyboardButton(text='Выбрать кафедру.')
keyboard_hi.add(key)

keyboard_admin = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=False, one_time_keyboard=True)
key = types.KeyboardButton(text='Начать новое интервью.')
keyboard_admin.add(key)
key = types.KeyboardButton(text='Выбрать одно из прошлых интервью.')
keyboard_admin.add(key)
key = types.KeyboardButton(text='Выбрать кафедру.')
keyboard_admin.add(key)
key = types.KeyboardButton(text='Назначить новое интервью.')
keyboard_admin.add(key)
