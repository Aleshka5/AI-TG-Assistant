import secrets
import string
from config import CLIENT_JSON_CONFIG, START_JSON_INTERVIEW
from src.ai_functools import get_addition_question, get_base_guestions

def print_welcome(owner):
    '''

    :param owner: Никнейм пользователя.
    :return: Выводит приветственные слова для старого пользователя.
    '''
    text = f'''Добро пожаловать, {owner}!
AI State: Assistant
Выберите пункт меню...
     
    '''
    return text

def print_hi_chat(owner):
    '''

    :param owner: Никнейм пользователя.
    :return: Выводит приветственные слова для старого пользователя.
    '''
    text = f'''Умный чат приветствует вас, {owner}!
AI State: Chat AI
Введи ваш вопрос и я постараюсь на него ответить.'''
    return text

def print_list_interviews(client_data):
    '''

    :param client_data: Профиль клиента.
    :return: Выводит меню выбора прошлого интервью.
    '''
    for query in client_data['Queries'].keys():
        pass
    if int(query) != 0:
        return f'''AI State: Helper\nВаши интервью:{[query for query in client_data['Queries'].keys() if query != '0']}'''
    else:
        return 'У вас пока не было ни одного интервью.'

def print_user_not_founded():
    return '''Добро пожаловать!
Введите /start, чтобы мы зарегистрировали вас и рассказали о возможностях нашего сервиса.
    '''

def print_no_parsed_data():
    return f'''Если хотите по общаться со мной на разные темы - введите /chat.
Если вы хотите вернуться к началу - введите /start.
Если вы не хотите этого, внимательно проверьте ваш запрос на соответствие формы ввода.
'''

def print_interview(interview_dict: dict):
    output = []
    pipeline = ['О1', 'Д1', 'О2', 'Д2', 'О3', 'Д3', 'О4', 'Д4', 'О5', 'Д5']
    for state in pipeline:
        output_line = ''
        if 'О' in state:
            output_line += interview_dict['AI'][state] + '\n'
        else:
            output_line += interview_dict['AI'][state]
        output_line += interview_dict['Client'][state] + '\n\n'
        output.append(output_line)
    return output

def print_question(question, state):
    '''
    Выводит первый вопрос из интервью.
    :return:
    '''
    str_0 = 'Дайте ответ на поставленный вопрос одним сообщением:'
    str_1 = 'Мне важно уточнить следующую информацию:'
    dict_fully_questions = {'О1':str_0, 'Д1':str_1, 'О2':str_0, 'Д2':str_1, 'О3':str_0, 'Д3':str_1, 'О4':str_0, 'Д4':str_1, 'О5':str_0, 'Д5':str_1}
    return dict_fully_questions[state]+'\n'+'Заглушка для вопроса\nВопрос: ' + question

def add_new_user():
    '''

    :param user_name: Никнейм пользователя.
    :param DATASET: Датасет, в который мы будет добавлять данные о новом пользователе.
    :return:
    '''
    client_base_config = CLIENT_JSON_CONFIG.copy()
    client_base_config['State'] = set_state('Helper')
    return client_base_config

def create_new_interview(client_data):
    previous_queries = client_data['Queries']
    print(previous_queries.keys())
    for query in previous_queries.keys():
        pass
    print(query)
    print(f'Создание интервью с номером {int(query)+1}')
    previous_queries[str(int(query) + 1)] = START_JSON_INTERVIEW
    return previous_queries, str(int(query) + 1)

def fill_base_questions(cilent_interview_data):
    new_cilent_interview_data = cilent_interview_data
    pipeline = ['О1', 'О2', 'О3', 'О4', 'О5']
    # TODO: заменить на генерацию вопросов
    template_questions = get_base_guestions()

    for state in range(len(pipeline)):
        new_cilent_interview_data['AI'][pipeline[state]] = template_questions[state]
    return new_cilent_interview_data

def interview(cilent_interview_data,client_answer = None):
    pipeline = ['О1', 'Д1', 'О2', 'Д2', 'О3', 'Д3', 'О4', 'Д4', 'О5', 'Д5']
    new_cilent_interview_data = cilent_interview_data
    # Если интервью только началось
    if not bool(new_cilent_interview_data['AI'][pipeline[0]]):
        new_cilent_interview_data = fill_base_questions(new_cilent_interview_data)
        print(f'Заполнили основные вопросы:{new_cilent_interview_data}')
    print(f'Изначальные данные интервью:{cilent_interview_data}')
    # поиск первого не пройденного этапа интервью
    for current in range(len(pipeline)):

        if not bool(new_cilent_interview_data['Client'][pipeline[current]]):
            
            # Если мы остановились на дополнительном вопросе
            if 'Д' in pipeline[current]:
                if client_answer is None:
                    break
                new_cilent_interview_data['Client'][pipeline[current]] = client_answer

            # Если мы остановились на основном вопросе
            elif 'О' in pipeline[current]:
                if client_answer is None:
                    break
                new_cilent_interview_data['Client'][pipeline[current]] = client_answer
                new_cilent_interview_data['AI'][pipeline[current+1]] = get_addition_question(new_cilent_interview_data['Client'][pipeline[current]])
                print(f'Ответили на доп вопрос {pipeline[current]} и выдали вопрос {print_question(new_cilent_interview_data["AI"][pipeline[current+1]],pipeline[current+1])}')

            if pipeline[current] == 'Д5':
                return new_cilent_interview_data, 'Интервью окончено'
            else:
                return new_cilent_interview_data, print_question(new_cilent_interview_data['AI'][pipeline[current+1]], pipeline[current+1])

    if client_answer:
        return new_cilent_interview_data, 'Интервью окончено'
    else:
        return new_cilent_interview_data, print_question(new_cilent_interview_data['AI'][pipeline[current]], pipeline[current])

def set_state(ai_state):
    '''

    :param ai_state: Название состояния, которое нужно установить для общения с текущим клиентом:
                    ['Interviewer','Helper','Chat','estimator']
    :return: Возвращает конструкцию с одним включенным режимом из перечисленных.
    '''
    new_ai_state_config = CLIENT_JSON_CONFIG['State'].copy()
    new_ai_state_config[ai_state] = True
    return new_ai_state_config

def get_state(ai_states: dict):
    '''

    :param ai_states: Конструкцию с одним включенным режимом из перечисленных:
                    ['Interviewer','Helper','Chat','estimator']
    :return: Возвращает название состояния, которое было установить для общения с текущим клиентом:
                    ['Interviewer','Helper','Chat','estimator']
    '''
    for state,able in ai_states.items():
        if able:
            return state

def generate_token(length=32):
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

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