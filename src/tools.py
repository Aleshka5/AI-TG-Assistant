# import secrets
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

# def print_list_interviews(client_data):
#     '''
#
#     :param client_data: Профиль клиента.
#     :return: Выводит меню выбора прошлого интервью.
#     '''
#     for query in client_data['Queries'].keys():
#         pass
#     if int(query) != 0:
#         return f'''AI State: Helper\nВаши интервью:{[query for query in client_data['Queries'].keys() if query != '0']}'''
#     else:
#         return 'У вас пока не было ни одного интервью.'


def print_user_not_founded():
    return '''Добро пожаловать!
Введите /start, чтобы мы зарегистрировали вас и рассказали о возможностях нашего сервиса.
    '''


def print_no_parsed_data():
    return f'''Если хотите по общаться со мной на разные темы - введите /chat.
Если вы хотите вернуться к началу - введите /start.
Если вы не хотите этого, внимательно проверьте ваш запрос на соответствие формы ввода.
'''

# Not to need
# def print_interview(interview_dict: dict):
#     output = []
#     pipeline = ['О1', 'Д1', 'О2', 'Д2', 'О3', 'Д3', 'О4', 'Д4', 'О5', 'Д5']
#     for state in pipeline:
#         output_line = ''
#         if 'О' in state:
#             output_line += interview_dict['AI'][state] + '\n'
#         else:
#             output_line += interview_dict['AI'][state]
#         output_line += interview_dict['Client'][state] + '\n\n'
#         output.append(output_line)
#     return output


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
    # alphabet = string.ascii_letters + string.digits
    # return ''.join(secrets.choice(alphabet) for _ in range(length))


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