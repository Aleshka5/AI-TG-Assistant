from . import db
from telebot import types
from src.ai_functools import get_addition_question, get_base_guestions, just_chat

def interview(user_name, user_answer=None):
    interview_id, interview_log = db.get_active_interview(user_name)
    interview_list = [text for text in interview_log.split('\n') if len(text)>0]
    print(interview_list)

    for message_id in range(len(interview_list)):
        if interview_list[message_id] == 'Ответ:None.':

            # Продолжение интервью
            if user_answer:
                interview_list[message_id] = f'Ответ:{user_answer}'

                # Если интервью окончено
                if message_id == len(interview_list) - 1:
                    db.write_interview(interview_id, interview_list)
                    db.finish_interview(interview_id)
                    return None

                question = interview_list[message_id + 1]
                db.write_interview(interview_id, interview_list)
                return question

            # Начало интервью
            else:
                question = interview_list[message_id - 1]
                db.write_interview(interview_id, interview_list)
                return question

def get_interviews_titles(user_name):
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=False, one_time_keyboard=True)
    titles = db.get_all_interviews(user_name)
    numbers = [i[0] for i in titles]
    titles = [i[1] for i in titles]
    titles = [f'{numbers[i]}. Выбрать {titles[i].lower()}' for i in range(len(titles))]
    if len(titles) > 0:
        for title in titles:
            keyboard.add(types.KeyboardButton(text=title))
        return keyboard
    else:
        return None

def get_log_interview(interview_id, uesr_name):
    interview_log = db.get_interview(interview_id, uesr_name)
    # interview_dict = dict(zip(cols_names, interview_log[0]))
    # res_print = ''
    # for i in range(1,6):
    #     res_print += interview_dict[f'quest{i}'] + '\n' + interview_dict[f'ans{i}'] + '\n'
    #     res_print += interview_dict[f'extraquest{i}'] + '\n' + interview_dict[f'extrans{i}'] + '\n'
    return interview_log


