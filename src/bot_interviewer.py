import re
from . import db
from telebot import types
from config import interview_columns
from src.ai_functools import get_addition_question, get_base_guestions, just_chat

def interview(user_name, user_answer=None):
    interview_log, cols_names = db.get_active_interview(user_name)
    interview_dict = dict(zip(cols_names,interview_log[0]))
    print(interview_dict)
    interview_id = interview_dict['id']

    for i in range(1,6):

        if interview_dict[f'ans{i}'] is None:

            # Продолжение интервью
            if user_answer:
                # Записать ответ
                print('Запишем:',user_answer)
                db.write_answer(interview_id, 'base', user_answer, i)
                # Задать доп вопрос
                add_question = get_addition_question(user_answer)
                # Записать вопрос
                db.write_a_question(interview_id, 'extra', add_question, i)
                return add_question

            # Начало интервью
            else:
                # Создать n основных вопросов
                base_questions = get_base_guestions()
                # Записать основные вопросы в базу
                db.write_questions(interview_id,base_questions)
                return base_questions[i-1]

        elif interview_dict[f'extrans{i}'] is None:

            # Записать ответ
            print('Запишем доп:', user_answer)
            db.write_answer(interview_id, 'extra', user_answer, i)
            if i < 5:
                # Выдать новый вопрос
                question = db.get_cur_question(interview_id, i+1)
                return question
            else:
                # Установить новое название для завершённого интервью
                db.finish_interview(interview_id)
                return None

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
    interview_log, cols_names = db.get_interview(interview_id, uesr_name)
    interview_dict = dict(zip(cols_names, interview_log[0]))
    res_print = ''
    for i in range(1,6):
        res_print += interview_dict[f'quest{i}'] + '\n' + interview_dict[f'ans{i}'] + '\n'
        res_print += interview_dict[f'extraquest{i}'] + '\n' + interview_dict[f'extrans{i}'] + '\n'
    return res_print


