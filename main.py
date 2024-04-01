import telebot
import re
from src import db
from src.bot_interviewer import interview, get_interviews_titles, get_log_interview
from src.tools import print_welcome, print_user_not_founded, print_hi_chat, print_no_parsed_data
from config import TOKEN, keyboard_hi, keyboard_admin,limit_text_len

telebot.apihelper.ENABLE_MIDDLEWARE = True
bot = telebot.TeleBot(TOKEN, parse_mode=None)

def main(token):
    telebot.apihelper.ENABLE_MIDDLEWARE = True
    bot = telebot.TeleBot(token, parse_mode=None)
    bot.polling()

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
    if db.user_verification(owner):
        bot.send_message(message.chat.id, print_hi_chat(owner=owner))
        # Изменить состояние бота
        db.set_bot_state(owner, 'Chat')

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
    if db.user_verification(owner):

        # Вывести приветствие
        if db.check_position(owner,['admin','company']):
            bot.send_message(message.chat.id, print_welcome(owner=owner), reply_markup=keyboard_admin)

        else:
            bot.send_message(message.chat.id, print_welcome(owner=owner), reply_markup=keyboard_hi)
        # Изменить состояние бота
        db.set_bot_state(owner, 'Assistant')

@bot.message_handler(content_types='text')
def get_any_message(message):
    db.init()
    owner = message.from_user.username

    # Проверка пользователя на наличие в чёрном списке
    if not db.user_verification(owner):
        bot.send_message(message.chat.id, "Извините, вы были заблокированы за нарушение правил. "
                                          "Попробуйте обратиться к @alekseyfilekov")
        return None

    text = message.text
    # Выбор типа парсинга сообщений
    # Парсер сценариев для помощи в навигации по возможностям сервиса
    bot_state = db.get_bot_state(owner)
    if bot_state == 'Assistant':

        # Начинаем новое интервью
        if 'Начать новое интервью.' == text:
            bot.send_message(message.chat.id, "Введите токен в формате:\n'Токен: xxx...xxx'")

        elif 'Токен:' in text:

            if db.check_token(owner,text[6:].strip()):
                db.set_enable_interview(text[6:].strip())
                db.set_bot_state(owner, 'Interviewer')
                question = interview(owner)
                bot.send_message(message.chat.id, question)

            else:
                bot.send_message(message.chat.id, "Вы ввели недействитеьный токен. Попробуйте ещё раз...")


        # Выбираем одно из прошлых интервью
        elif 'Выбрать одно из прошлых интервью.' == text:
            keyboard_interviews = get_interviews_titles(owner)
            if keyboard_interviews:
                bot.send_message(message.chat.id, 'Выбери одно из предыдущих интервью:', reply_markup=keyboard_interviews)
            else:
                bot.send_message(message.chat.id, 'Не найдено ни одного интервью.', reply_markup=keyboard_interviews)

        elif 'Назначить новое интервью.' == text:
            bot.send_message(message.chat.id, "Введите имя работника в формате:\nИмя: @alekseyfilenkov")

        elif 'Имя:' in text:
            user_name = text[4:].strip().strip('@')
            token = db.add_token(owner,user_name)
            if token:
                bot.send_message(message.chat.id, f"Передайте сотруднику\nToken:{token}")
            else:
                bot.send_message(message.chat.id, "Ошибка, проверьте имя и попробуйте ещё раз.")

        elif 'Назад' in text:
            pass

        # Продолжение интервью
        elif 'Выбрать не законченное интервью' in text:
            db.set_bot_state(owner, 'Interviewer')
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
                bot.send_message(message.chat.id, print_log)

        else:
            bot.send_message(message.chat.id, print_no_parsed_data())

    # Парсер сценариев для ведения интервью
    elif bot_state == 'Interviewer':
        # Проверка текста на лимит, если не пройдена - заблокировать пользователя.
        if len(text) > limit_text_len:
            bot.send_message(message.chat.id, 'Вы написали очень большое сообщение.')
            db.ban_user(owner)
            return None

        # Запуск функции проведения интервью
        question = interview(owner, text)
        if question:
            print(question)
            bot.send_message(message.chat.id, question)
            db.select_all()
        else:
            db.set_bot_state(owner, 'Assistant')
            bot.send_message(message.chat.id, 'Интервью окончено.')


    elif bot_state == 'Chat':
        bot.send_message(message.chat.id, text)

    else:
        bot.send_message(message.chat.id, print_user_not_founded())

    return None

def main():
    bot.polling()

if __name__ == '__main__':
    bot.polling()

