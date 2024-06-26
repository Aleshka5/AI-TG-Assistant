import telebot
import re
from threading import Thread
from telebot import types
from src import db
from src.ai_functools import just_chat, ai_analize
from src.bot_interviewer import interview, get_interviews_titles, get_log_interview
from src.tools import print_welcome, print_hi_chat, print_no_parsed_data, get_chairs_list
from config import (keyboard_hi, keyboard_admin, keyboard_chairs, limit_text_len, USER_NOT_FOUNDED,
                    NEW_USER_UNKNOWN_INPUT, TEXT_LEN_LIMIT_ERROR, BAN_APOLOGISE, TOKEN_TRY_AGAIN)

def bot_start(tg_token: str, ai_token: str):
    '''
    Функция запускает сервис для работы телеграм бота-интервьюера.
    :param tg_token: Токен для Telegram бота.
    :param ai_token: Токен для Open AI Chat-GPT-3.5-Turbo.
    :return:
    '''
    telebot.apihelper.ENABLE_MIDDLEWARE = True
    bot = telebot.TeleBot(tg_token, parse_mode=None)

    @bot.message_handler(commands=['chat'])
    def chat_welcome(message):
        '''

        :param message: Объект входного сообщения.
        :param DATASET: Данные по истории обращений к сервису в формате json (dict).
        :return: Возвращает приветственное сообщение и переводит AI помощника в состояние Helper (помощник)
        '''
        db.init()
        owner = message.from_user.username
        # Проверить на Black list
        if db.user_verification(owner, message.text):
            # Отправить приветствие пользователю
            bot.send_message(message.chat.id, print_hi_chat(owner=message.from_user.first_name))
            # Изменить состояние бота
            db.set_bot_state(owner, 'Chat', bot, message)

    @bot.message_handler(commands=['start'])
    def start_welcome(message):
        '''

        :param message: Объект входного сообщения.
        :param DATASET: Данные по истории обращений к сервису в формате json (dict).
        :return: Возвращает приветственное сообщение и переводит AI помощника в состояние Helper (помощник)
        '''
        db.init()
        owner = message.from_user.username

        # Проверить на Black list
        if db.user_verification(owner, message.text):

            # Вывести приветствие
            if db.check_position(owner, ['admin', 'company']):
                bot.send_message(message.chat.id, print_welcome(owner=message.from_user.first_name),
                                                                reply_markup=keyboard_admin)

            else:
                bot.send_message(message.chat.id, print_welcome(owner=message.from_user.first_name),
                                                                reply_markup=keyboard_hi)
            # Изменить состояние бота
            db.set_bot_state(owner, 'Assistant', bot, message)

    @bot.message_handler(content_types='text')
    def get_any_message(message):
        db.init()
        owner = message.from_user.username
        text = message.text

        # Проверка пользователя на наличие в чёрном списке
        verification = db.user_verification(owner, text)

        if not verification:
            bot.send_message(message.chat.id,BAN_APOLOGISE)
            return None

        # Если мы получили текст возвращения из бана
        elif isinstance(verification, str):
            bot.send_message(message.chat.id, verification)
            # Зануляем текст, чтобы не использовать процедуру возвращения в качестве ответа на вопрос
            text = None

        # Проверка текста на лимит, если не пройдена - заблокировать или предупредить пользователя.
        elif len(text) > limit_text_len:
            bot.send_message(message.chat.id, TEXT_LEN_LIMIT_ERROR)
            db.ban_user(owner)
            return None

        # Выбор типа парсинга сообщений
        # Парсер сценариев для помощи в навигации по возможностям сервиса
        bot_state = db.get_bot_state(owner)
        if bot_state == 'Assistant':

            # Начинаем новое интервью
            if 'Начать новое интервью.' == text:
                bot.send_message(message.chat.id, "Введите токен в формате:\n'Токен: xxx...xxx'")

            elif 'Выбрать кафедру.' == text:
                actual_chairs = keyboard_chairs
                for chair in get_chairs_list():
                    print(chair)
                    key = types.KeyboardButton(text=chair)
                    actual_chairs.add(key)
                bot.send_message(message.chat.id, "Выберите одну из предложенных кафедр:", reply_markup=actual_chairs)

            # Проверка введённого токена для интервью
            elif 'Токен:' in text:
                if db.get_chair_name(owner):
                    if db.check_token(owner, text[6:].strip()):
                        if db.set_enable_interview(owner, token=text[6:].strip()):
                            db.set_bot_state(owner, 'Interviewer', bot, message)
                            question = interview(owner)
                            bot.send_message(message.chat.id, question)
                        else:
                            bot.send_message(message.chat.id, 'Невозможно начать новое интервью.')

                    else:
                        bot.send_message(message.chat.id, TOKEN_TRY_AGAIN)
                else:
                    bot.send_message(message.chat.id, 'Не удалось определить вашу кафедру. Введите данные и попробуте снова...')

            # Выбираем одно из прошлых интервью
            elif 'Выбрать одно из прошлых интервью.' == text:

                keyboard_interviews = get_interviews_titles(owner)

                if keyboard_interviews:
                    bot.send_message(message.chat.id, 'Выбери одно из предыдущих интервью:',
                                     reply_markup=keyboard_interviews)

                else:
                    bot.send_message(message.chat.id, 'Не найдено ни одного интервью.',
                                     reply_markup=keyboard_interviews)

            elif 'Назначить новое интервью.' == text:
                bot.send_message(message.chat.id, "Введите имя работника в формате:\nИмя: @alekseyfilenkov")

            elif 'Имя:' in text:
                user_name = text[4:].strip().strip('@')
                token = db.add_token(owner, user_name)

                if token:
                    bot.send_message(message.chat.id, f"Передайте сотруднику\nТокен:{token}")

                else:
                    bot.send_message(message.chat.id, USER_NOT_FOUNDED)

            elif 'Назад' in text:
                pass

            elif 'Выбрать не начатое интервью' in text:
                pattern = r"^(.*?)\."
                match = re.search(pattern, text)

                # Если найдено соответствие, выводим найденную подстроку
                if match:
                    interview_id = int(match.group(1))
                    bot.send_message(message.chat.id, 'Введите токен в следующем формате:\nТокен:')

                    # if db.set_enable_interview(owner, interview_id=interview_id):
                    #     db.set_bot_state(owner, 'Interviewer', bot, message)
                    #     question = interview(owner)
                    #     bot.send_message(message.chat.id, question)
                    # else:
                    #     bot.send_message(message.chat.id, 'Невозможно начать новое интервью.')

            # Продолжение интервью
            elif 'Выбрать не законченное интервью' in text:
                db.set_bot_state(owner, 'Interviewer', bot, message)
                question = interview(owner)

                if question:
                    bot.send_message(message.chat.id, question)

                else:
                    bot.send_message(message.chat.id, 'Это интервью было завершено.')

            elif 'Выбрать завершённое интервью' in text:
                pattern = r"^(.*?)\."
                match = re.search(pattern, text)

                # Если найдено соответствие, выводим найденную подстроку
                if match:
                    interview_id = int(match.group(1))
                    print_log = get_log_interview(interview_id, owner)
                    # Если анализ ещё не запускался
                    if print_log[1] is None:
                        chair_name = db.get_chair_name(owner)
                        db.write_analyze(interview_id, 'Analyze in process...')
                        Thread(target=ai_analize, args=(interview_id, print_log[0], chair_name, ai_token)).start()
                        # Вывести кнопки /start
                        if db.check_position(owner, ['admin', 'company']):
                            bot.send_message(message.chat.id, print_log[0]+'\nИнтервью отправлено на анализ ИИ.',
                                             reply_markup=keyboard_admin)
                        else:
                            bot.send_message(message.chat.id, print_log[0]+'\nИнтервью отправлено на анализ ИИ.',
                                             reply_markup=keyboard_hi)

                    else:
                        # Вывести кнопки /start
                        if db.check_position(owner, ['admin', 'company']):
                            bot.send_message(message.chat.id, print_log[0]+print_log[1],
                                             reply_markup=keyboard_admin)
                        else:
                            bot.send_message(message.chat.id, print_log[0]+print_log[1],
                                             reply_markup=keyboard_hi)
            else:

                for chair in get_chairs_list():

                    if text == chair:
                        db.update_chair_name(owner, chair)
                        # Вывести кнопки /start
                        if db.check_position(owner, ['admin', 'company']):
                            bot.send_message(message.chat.id, f"За вами зафиксирована кафедра: {chair}",
                                             reply_markup=keyboard_admin)
                        else:
                            bot.send_message(message.chat.id, f"За вами зафиксирована кафедра: {chair}",
                                             reply_markup=keyboard_hi)

                        return None
                bot.send_message(message.chat.id, print_no_parsed_data())


        # Парсер сценариев для ведения интервью
        elif bot_state == 'Interviewer':
            # Запуск функции проведения интервью
            question = interview(owner, text)
            if question:
                bot.send_message(message.chat.id, question)

            else:
                db.set_bot_state(owner, 'Assistant', bot, message)
                bot.send_message(message.chat.id, 'Интервью окончено. Спасибо за честные и развёрнутые ответы.')


        elif bot_state == 'Chat':
            bot.send_message(message.chat.id, just_chat(text, token=ai_token))
            # top3_answers = just_chat(text,'RV_all')
            # bot.send_message(message.chat.id, top3_answers[0])
            # bot.send_message(message.chat.id, top3_answers[1])
            # bot.send_message(message.chat.id, top3_answers[2])
            # bot.send_message(message.chat.id, f'Я бы вам ответил на: {text}, но в данный мемент нет связи с API.')

        else:
            bot.send_message(message.chat.id, NEW_USER_UNKNOWN_INPUT)

        return None

    bot.polling()


if __name__ == '__main__':
    import os
    from pickle import load

    if os.path.exists('TOKEN.pkl') and os.path.exists('AI_TOKEN.pkl'):
        with open('TOKEN.pkl', 'rb') as f:
            TG_TOKEN = load(f)

        with open('AI_TOKEN.pkl', 'rb') as f:
            AI_TOKEN = load(f)
        bot_start(TG_TOKEN,AI_TOKEN)
    else:
        print('Токен не найден...')
