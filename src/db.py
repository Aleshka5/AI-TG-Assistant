import sqlite3
import os
from src.tools import generate_token, print_table
from config import interview_columns
def db_connection(func):
    def wrapper(*args,**kwargs):
        # Выполнение некой функции
        conn = sqlite3.connect('./dataset/my_database.db')
        cursor = conn.cursor()
        response = func(*args,**kwargs,cursor=cursor)
        conn.commit()
        conn.close()
        return response
    return wrapper

@db_connection
def init(cursor=None):
    '''
    Создаёт при необходимости все нужные для работы таблицы.
    :return:
    '''
    # my_file = Path("../dataset/my_database.db")
    # if os.path.exists("../dataset/my_database.db"):
    #     print('Exists')
    #     return None

    # Создание таблицы Employees
    cursor.execute('''CREATE TABLE IF NOT EXISTS Employees (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            name char(100),
                            position char(50),
                            bot_state char(11),
                            enable BOOL DEFAULT True
                        );''')

    # Создание таблицы Tokens с внешним ключом на таблицу Employees
    cursor.execute('''CREATE TABLE IF NOT EXISTS Tokens (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            token char(256),
                            emp_id INTEGER,
                            quest1 TEXT, extraquest1 TEXT, 
                            quest2 TEXT, extraquest2 TEXT, 
                            quest3 TEXT, extraquest3 TEXT, 
                            quest4 TEXT, extraquest4 TEXT, 
                            quest5 TEXT, extraquest5 TEXT,
                            ans1 TEXT, extrans1 TEXT, 
                            ans2 TEXT, extrans2 TEXT, 
                            ans3 TEXT, extrans3 TEXT, 
                            ans4 TEXT, extrans4 TEXT, 
                            ans5 TEXT, extrans5 TEXT,
                            summary TEXT,
                            title char(30) DEFAULT 'Не законченное интервью',
                            interview_enable BOOL DEFAULT False,
                            deleted BOOL DEFAULT False,
                            FOREIGN KEY (emp_id) REFERENCES Employees(id)
                        );''')

    cursor.execute('''INSERT INTO Employees (name, position)
                        SELECT 'alekseyfilenkov', 'admin'
                        WHERE NOT EXISTS (
                        SELECT 1 FROM Employees WHERE name = 'alekseyfilenkov'
                        );''')
    return None

@db_connection
def check_token(user_name: str, token: str, cursor=None):
    '''
    Проверка что у конкретного пользователя нет активных интервью и предоставленный токен закреплён именно за ним.
    :param token: токен для прохождения интервью предоставленный работником.
    :return: (bool) Допущен ли пользователь до интервью.
    '''
    cursor.execute('''SELECT Tokens.interview_enable
                        FROM Employees INNER JOIN Tokens 
                        ON Employees.id = Tokens.emp_id
                        WHERE Tokens.interview_enable = 1''')
    response = cursor.fetchall()
    if len(response) == 0:
        cursor.execute('''SELECT Employees.name
                                FROM Employees
                                INNER JOIN Tokens ON Employees.id = Tokens.emp_id
                                WHERE Tokens.token = ?''', (token,))
        response = cursor.fetchall()
        if len(response) > 0:
            if response[0][0] == user_name:
                return True

        print('Это не верный токен.')
        return False

    else:
        print('У вас больше одного активного интервью')
        return False

@db_connection
def set_enable_interview(token: str, cursor=None):
    cursor.execute('''UPDATE Tokens SET interview_enable = 1 WHERE token = ?''', (token,))
    return None

@db_connection
def get_active_interview(user_name: str, cursor=None):
    cursor.execute('''SELECT Tokens.id,
                            Tokens.ans1, Tokens.extrans1,
                            Tokens.ans2, Tokens.extrans2,
                            Tokens.ans3, Tokens.extrans3,
                            Tokens.ans4, Tokens.extrans4,
                            Tokens.ans5, Tokens.extrans5 FROM Employees INNER JOIN Tokens 
                            ON Employees.id = Tokens.emp_id
                            WHERE Tokens.interview_enable = 1 AND Employees.name = ?''',(user_name,))
    response = cursor.fetchall()
    column_names = [description[0] for description in cursor.description]
    return response, column_names

@db_connection
def get_interview(interview_id, user_name: str, cursor=None):
    cursor.execute('''SELECT Tokens.quest1, Tokens.extraquest1,
                            Tokens.quest2, Tokens.extraquest2,
                            Tokens.quest3, Tokens.extraquest3,
                            Tokens.quest4, Tokens.extraquest4,
                            Tokens.quest5, Tokens.extraquest5,
                            Tokens.ans1, Tokens.extrans1,
                            Tokens.ans2, Tokens.extrans2,
                            Tokens.ans3, Tokens.extrans3,
                            Tokens.ans4, Tokens.extrans4,
                            Tokens.ans5, Tokens.extrans5 FROM Employees INNER JOIN Tokens 
                            ON Employees.id = Tokens.emp_id
                            WHERE Tokens.id = ? AND Employees.name = ?''',(interview_id, user_name))
    response = cursor.fetchall()
    column_names = [description[0] for description in cursor.description]
    return response, column_names

@db_connection
def get_all_interviews(user_name: str, cursor=None):
    cursor.execute('''SELECT Tokens.id, Tokens.title FROM Employees INNER JOIN Tokens 
                            ON Employees.id = Tokens.emp_id
                            WHERE Employees.name = ?''',(user_name,))
    response = cursor.fetchall()
    print(response)
    return response

@db_connection
def add_user(user_name: str, position: str, cursor=None):
    '''
    Добавляет в БД нового пользователя.
    :param user_name: (str) - имя нового пользователя
    :return: None
    '''
    cursor.execute('''INSERT INTO Employees (name,position) VALUES (?,?)''', (user_name,position))
    return None

@db_connection
def ban_user(user_name: str, cursor=None):
    '''
    Добавление пользователя в чурный список.
    :param user_name: (str) - имя пользователя
    :return: None
    '''
    cursor.execute('''UPDATE Employees SET enable = 0 WHERE name = ?''', (user_name,))
    return None

@db_connection
def get_user_id(user_name: str, cursor=None):
    cursor.execute('''SELECT Employees.id FROM Employees WHERE Employees.name = ?''', (user_name,))
    user_id = cursor.fetchall()
    if len(user_id) > 0:
        return user_id[0][0]
    else:
        return None

def user_verification(user_name: str):
    '''
    Проверка на наличие пользователя в чёрном списке.
    :param user_name: Имя пользователя.
    :return: (bool) True - пользователь прошёл верификацию.
                    False - пользователю отказано в доступе к сервису.
    '''
    conn = sqlite3.connect('./dataset/my_database.db')
    cursor = conn.cursor()
    cursor.execute('''SELECT Employees.enable FROM Employees WHERE Employees.name = ?''', (user_name,))
    response = cursor.fetchall()
    conn.commit()
    conn.close()
    if len(response) == 0:
        if user_name == 'alekseyfilenkov':
            add_user(user_name, 'admin')
        else:
            add_user(user_name, 'employee')
        return True
    elif response[0][0] == 1:
        return True
    else:
        return False

@db_connection
def check_position(user_name: str, position: list, cursor=None):
    cursor.execute('''SELECT Employees.position FROM Employees WHERE Employees.name = ?''', (user_name,))
    response = cursor.fetchall()
    if response[0][0] in position:
        return True
    else:
        return False

@db_connection # TODO:
def add_token(user_name, employee_name, cursor=None):
    if check_position(user_name,['admin','company']):
        employee_id = get_user_id(employee_name)
        if employee_id:
            token = generate_token(length=256)
            cursor.execute('''INSERT INTO Tokens (token,emp_id) VALUES (?,?)''', (token,employee_id))
            return token
        else:
            print('Не найден такой сотрудник.')
            return None
    # Вернуть отказано в разрешении
    else:
        print('permission denied')
        return None

@db_connection
def select_all(cursor=None):
    cursor.execute('''SELECT * FROM Employees LEFT JOIN Tokens ON Employees.id == Tokens.emp_id''')
    response = cursor.fetchall()
    column_names = [description[0] for description in cursor.description]
    print_table(response,column_names)

@db_connection
def set_bot_state(user_name, new_state, cursor=None):
    cursor.execute('''UPDATE Employees SET bot_state = ? WHERE name = ?;''',(new_state,user_name))
    return None

@db_connection
def get_bot_state(user_name, cursor=None):
    cursor.execute('''SELECT Employees.bot_state FROM Employees WHERE name == ?;''',(user_name,))
    response = cursor.fetchall()
    return response[0][0]

@db_connection
def write_a_question(interview_id, quest_type, question, quest_id, cursor=None):
    if quest_type == 'base':
        cursor.execute(f'''UPDATE Tokens SET quest{quest_id} = ? WHERE id = ?''',(question,interview_id))
    elif quest_type == 'extra':
        cursor.execute(f'''UPDATE Tokens SET extraquest{quest_id} = ? WHERE id = ?''', (question, interview_id))

@db_connection
def write_questions(interview_id, questions, cursor=None):
    query = f'''UPDATE Tokens SET '''
    for i in range(1,len(questions)+1):
        query += f"quest{i} = '{questions[i-1]}',"
    query = query[:-1] + f' WHERE id = {interview_id}'
    # print(query)
    cursor.execute(query)

@db_connection
def get_cur_question(interview_id, question_id,cursor=None):
    cursor.execute(f'''SELECT quest{question_id} FROM Tokens WHERE id = ?''',(interview_id,))
    response = cursor.fetchall()
    if len(response) > 0:
        return response[0][0]
    else:
        return None

@db_connection
def write_answer(interview_id, ans_type, answer, answer_id, cursor=None):
    if ans_type == 'base':
        print(f'''UPDATE Tokens SET ans{answer_id} = '{answer}' WHERE id = {interview_id};''')
        cursor.execute(f'''UPDATE Tokens SET ans{answer_id} = ? WHERE id = ?;''',(answer,interview_id))
    elif ans_type == 'extra':
        print(f'''UPDATE Tokens SET extrans{answer_id} = '{answer}' WHERE id = {interview_id};''')
        cursor.execute(f'''UPDATE Tokens SET extrans{answer_id} = ? WHERE id = ?;''', (answer, interview_id))

@db_connection
def finish_interview(interview_id, cursor=None):
    cursor.execute(f'''UPDATE Tokens SET title = 'Завершённое интервью', interview_enable = False WHERE id = ?''', (interview_id,))

if __name__ == '__main__':
    init()
    select_all()
