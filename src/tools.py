import os
import hashlib
from datetime import datetime


def print_welcome(owner):
    '''

    :param owner: Никнейм пользователя.
    :return: Выводит приветственные слова для старого пользователя.
    '''
    text = f'''Добро пожаловать, {owner}!
Выберите пункт меню...
     
    '''
    return text


def print_hi_chat(owner):
    '''

    :param owner: Никнейм пользователя.
    :return: Выводит приветственные слова для старого пользователя.
    '''
    text = f'''Умный чат приветствует вас, {owner}!
Введи ваш вопрос и я постараюсь на него ответить.'''
    return text


def print_user_not_founded():
    return '''Добро пожаловать!
Введите /start, чтобы мы зарегистрировали вас и рассказали о возможностях нашего сервиса.
    '''


def print_no_parsed_data():
    return f'''Если хотите по общаться со мной на разные темы - введите /chat.
Если вы хотите вернуться к началу - введите /start.
Если вы не хотите этого, внимательно проверьте ваш запрос на соответствие формы ввода.
'''


def print_question(question, state):
    '''
    Выводит первый вопрос из интервью.
    :return:
    '''
    str_0 = 'Дайте ответ на поставленный вопрос одним сообщением:'
    str_1 = 'Мне важно уточнить следующую информацию:'
    dict_fully_questions = {'О1':str_0, 'Д1':str_1, 'О2':str_0, 'Д2':str_1, 'О3':str_0, 'Д3':str_1, 'О4':str_0, 'Д4':str_1, 'О5':str_0, 'Д5':str_1}
    return dict_fully_questions[state]+'\n'+'Заглушка для вопроса\nВопрос: ' + question


def generate_token():
    return hashlib.md5(str(datetime.now()).encode()).hexdigest()


def print_table(table_list,columns_list):
    '''
    :param table_list: - массив с данными таблицы
    :param columns_list:  - массив в котором лежат значения столбцов в нужном порядке
    :return: None
    '''
    # Проверка на соответствие количества столбцов
    assert len(table_list[0]) == len(columns_list)

    table_list = list(map(list, table_list))
    raw_limit = 50
    # Расчёт длинн столбцов
    len_list = []
    for column in range(len(table_list[0])):
        max = 0
        for raw in range(len(table_list)):
            if len(str(table_list[raw][column])) > max:
                max = len(str(table_list[raw][column]))
                if max > raw_limit:
                    max = raw_limit
                    table_list[raw][column] = str(table_list[raw][column])[:raw_limit-3] + '...'
        if max < len(str(columns_list[column])):
            max = len(str(columns_list[column]))

        len_list.append(max)

    # Расчёт полной длинный таблицы
    finally_len = 0
    for i in len_list:
        finally_len += i

    # Вывод названий столбцов
    for column in range(len(columns_list)):
        print(str(' {:'+f'^{len_list[column]}'+'} |').format(columns_list[column]),end='')
    print('\n'+'-' * (finally_len+len(columns_list)*3))

    # Вывод данных таблицы
    for raw in range(len(table_list)):
        for column in range(len(table_list[0])):
            print(str(' {:'+f'^{len_list[column]}'+'} |').format(str(table_list[raw][column])),end='')
        print('')
    return None


def get_chairs_list() -> list:
    return [file[:-4] for file in os.listdir('./chairs_data/') if '.txt' in file]


def get_questions(folder_path: str = './Blanks/') -> list:
    blanks = [file for file in os.listdir(folder_path) if 'Blank' in file]
    questions_dict = {}
    zero_nine = tuple(map(str, list(range(0, 10))))
    one_ten = list(map(str, list(range(1, 11))))
    for n in range(1,len(blanks)+1):
        with open(f'{folder_path}/Blank_p{n}.txt', 'r') as file:
            current_line = None
            for line in file:
                line = line.strip('\n')
                if len(line) > 0:

                    # Delete all mark lines
                    if line.split('\t') == one_ten:
                        continue

                    # Get a cluster of the questions
                    if line[0] in zero_nine:
                        current_line = ''.join([word + ' ' for word in line.split()[1:]])
                        questions_dict[current_line] = []

                    # Get a question
                    elif current_line:
                        questions_dict[current_line].append(line)

    question_number = 0
    questions = []
    for key, items in questions_dict.items():
        question_number += 1
        for item in items:
            questions.append(
                f'{question_number}. Тема вопроса: {key}. {item}. Дайте оценку от 1 до 10 и опишите своё решение письменным комментарием.')
            questions.append('Ответ:None.')
    return questions

if __name__ == '__main__':
    print(get_questions())