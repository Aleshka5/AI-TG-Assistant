import telebot
import re
from src import db
from src.bot_interviewer import interview, get_interviews_titles, get_log_interview
from src.tools import print_welcome, print_user_not_founded, print_hi_chat, print_no_parsed_data
from config import (keyboard_hi, keyboard_admin,limit_text_len, USER_NOT_FOUNDED, NEW_USER_UNKNOWN_INPUT, TEXT_LEN_LIMIT_ERROR)

def bot_start(token):
    telebot.apihelper.ENABLE_MIDDLEWARE = True
    bot = telebot.TeleBot(token, parse_mode=None)

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
            bot.send_message(message.chat.id, print_hi_chat(owner=owner))
            # Изменить состояние бота
            db.set_bot_state(owner, 'Chat', bot, message)

    @bot.message_handler(commands=['start'])
    def send_welcome(message):
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
            if db.check_position(owner,['admin','company']):
                bot.send_message(message.chat.id, print_welcome(owner=owner), reply_markup=keyboard_admin)

            else:
                bot.send_message(message.chat.id, print_welcome(owner=owner), reply_markup=keyboard_hi)
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
            bot.send_message(message.chat.id,"Извините, вы были заблокированы за нарушение правил.\nДля разблокировки вам необходимо написать: Вернуться")
            return None

        # Если мы получили текст возвращения из бана
        elif isinstance(verification,str):
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

            # Проверка введённого токена для интервью
            elif 'Токен:' in text:

                if db.check_token(owner,text[6:].strip()):
                    if db.set_enable_interview(owner, token=text[6:].strip()):
                        db.set_bot_state(owner, 'Interviewer', bot, message)
                        question = interview(owner)
                        bot.send_message(message.chat.id, question)
                    else:
                        bot.send_message(message.chat.id, 'Невозможно начать новое интервью.')

                else:
                    bot.send_message(message.chat.id, "Вы ввели недействитеьный токен или у вас больше одного активного интервью. Попробуйте ещё раз...")

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
                token = db.add_token(owner,user_name)

                if token:
                    bot.send_message(message.chat.id, f"Передайте сотруднику\nToken:{token}")

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
                    if db.set_enable_interview(owner, interview_id=interview_id):
                        db.set_bot_state(owner, 'Interviewer', bot, message)
                        question = interview(owner)
                        bot.send_message(message.chat.id, question)
                    else:
                        bot.send_message(message.chat.id, 'Невозможно начать новое интервью.')

            # Продолжение интервью
            elif 'Выбрать не законченное интервью' in text:
                db.set_bot_state(owner, 'Interviewer', bot, message)
                question = interview(owner)

                if question:
                    bot.send_message(message.chat.id, question)

                else:
                    bot.send_message(message.chat.id, 'Это интервью было завершено.')

            elif 'Выбрать завершённое интервью' in text:
                # TODO: Вывод всего интервью.
                pattern = r"^(.*?)\."
                match = re.search(pattern, text)

                # Если найдено соответствие, выводим найденную подстроку
                if match:
                    interview_id = int(match.group(1))
                    print_log = get_log_interview(interview_id, owner)
                    # Вывести кнопки /start
                    if db.check_position(owner, ['admin', 'company']):
                        bot.send_message(message.chat.id, print_log, reply_markup=keyboard_admin)
                    else:
                        bot.send_message(message.chat.id, print_log, reply_markup=keyboard_hi)

            else:
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
            bot.send_message(message.chat.id, f'Я бы вам ответил на: {text}, но в данный мемент нет связи с API.')

        else:
            bot.send_message(message.chat.id, NEW_USER_UNKNOWN_INPUT)

        return None

    bot.polling()

def main():
    bot.polling()

if __name__ == '__main__':
    import os
    from pickle import load
    if os.path.exists('TOKEN.pkl'):
        with open('TOKEN.pkl','rb') as f:
            TOKEN = load(f)
        bot_start(TOKEN)
    else:
        print('Токен не найден...')

