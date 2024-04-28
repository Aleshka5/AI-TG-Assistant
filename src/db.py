import sqlite3
from src.tools import generate_token, print_table
from dataset import get_dataset_path
from config import INTERVIEW_BLANK, AI_STATE_ASSISTANT, AI_STATE_CHAT, AI_STATE_INTERVIEWER

def db_connection(func):
    def wrapper(*args, **kwargs):
        # Выполнение некой функции
        if get_dataset_path(new=False):
            conn = sqlite3.connect(get_dataset_path())
        else:
            conn = sqlite3.connect(get_dataset_path(new=True))
        cursor = conn.cursor()
        response = func(*args, **kwargs, cursor=cursor)
        conn.commit()
        conn.close()
        return response

    return wrapper

# TODO:Добавить в базу данные кафедры, к которой принадлежит пользователь
@db_connection
def init(cursor=None):
    '''
    Создаёт при необходимости все нужные для работы таблицы.
    :return:
    '''

    # Создание таблицы Employees
    cursor.execute('''CREATE TABLE IF NOT EXISTS Employees (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            name char(100),
                            position char(50),
                            bot_state char(11),
                            chair_name char(50),
                            enable integer DEFAULT 1
                        );''')

    # Создание таблицы Tokens с внешним ключом на таблицу Employees
    cursor.execute('''CREATE TABLE IF NOT EXISTS Tokens (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            token char(32),
                            emp_id INTEGER,
                            interview TEXT,
                            summary TEXT,
                            title char(30) DEFAULT 'Не начатое интервью',
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
    """
    Проверка что у конкретного пользователя нет активных интервью и предоставленный токен закреплён именно за ним.
    :param token: токен для прохождения интервью предоставленный работником.
    :return: (bool) Допущен ли пользователь до интервью.
    """
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
def set_enable_interview(user_name: str, token: str = None, interview_id: int = None, cursor=None):
    blank_interview_log = ''.join([message + '\n' for message in INTERVIEW_BLANK])
    # Проверяем нет ли активного интервью.
    cursor.execute('''SELECT Tokens.interview_enable FROM Employees INNER JOIN Tokens 
                                ON Employees.id = Tokens.emp_id
                                WHERE Tokens.interview_enable = 1 AND Employees.name = ?''', (user_name,))
    response = cursor.fetchall()
    # Если есть активное интервью - не создаём новое
    if len(response) > 0:
        return False

    # Активируем интервью
    if token:
        cursor.execute(
            "UPDATE Tokens SET interview_enable = 1, title = 'Не законченное интервью',interview = ? WHERE token = ?",
            (blank_interview_log, token))
        return True
    elif interview_id:
        cursor.execute(
            "UPDATE Tokens SET interview_enable = 1, title = 'Не законченное интервью', interview = ? WHERE id = ?",
            (blank_interview_log, interview_id))
        return True

    return False

@db_connection
def get_active_interview(user_name: str, cursor=None):
    cursor.execute('''SELECT Tokens.id, Tokens.interview FROM Employees INNER JOIN Tokens 
                            ON Employees.id = Tokens.emp_id
                            WHERE Tokens.interview_enable = 1 AND Employees.name = ?''', (user_name,))
    response = cursor.fetchall()
    print(response)
    return response[0][0], response[0][1]

@db_connection
def get_interview(interview_id, user_name: str, cursor=None):
    cursor.execute('''SELECT Tokens.interview FROM Employees INNER JOIN Tokens 
                            ON Employees.id = Tokens.emp_id
                            WHERE Tokens.id = ? AND Employees.name = ?''', (interview_id, user_name))
    response = cursor.fetchall()
    return response[0][0]

@db_connection
def get_all_interviews(user_name: str, cursor=None):
    cursor.execute('''SELECT Tokens.id, Tokens.title FROM Employees INNER JOIN Tokens 
                            ON Employees.id = Tokens.emp_id
                            WHERE Employees.name = ?''', (user_name,))
    response = cursor.fetchall()
    print(response)
    return response


@db_connection
def add_user(user_name: str, position: str, cursor=None):
    """
    Добавляет в БД нового пользователя.
    :param user_name: (str) - имя нового пользователя
    :return: None
    """
    cursor.execute('''INSERT INTO Employees (name,position) VALUES (?,?)''', (user_name, position))
    return None


@db_connection
def ban_user(user_name: str, cursor=None):
    """
    Добавление пользователя в чурный список.
    :param user_name: (str) - имя пользователя
    :return: None
    """
    cursor.execute('''UPDATE Employees SET enable = 2 WHERE name = ?''', (user_name,))
    return None


@db_connection
def get_user_id(user_name: str, cursor=None):
    cursor.execute('''SELECT Employees.id FROM Employees WHERE Employees.name = ?''', (user_name,))
    user_id = cursor.fetchall()
    if len(user_id) > 0:
        return user_id[0][0]
    else:
        return None


@db_connection
def user_verification(user_name: str, user_message: str, cursor=None):
    """
    Проверка на наличие пользователя в чёрном списке.
    :param user_name: Имя пользователя.
    :return: (bool) True - пользователь прошёл верификацию.
                    False - пользователю отказано в доступе к сервису.
    """
    cursor.execute('''SELECT Employees.enable FROM Employees WHERE Employees.name = ?''', (user_name,))
    response = cursor.fetchall()
    # Если пользователь не зарегестрирован
    if len(response) == 0:
        cursor.execute('''INSERT INTO Employees (name,position) VALUES (?,?)''', (user_name, 'employee'))
        return True
    # Если пользователь активен
    elif response[0][0] == 1:
        return True
    # Если пользователь заблокирован
    elif response[0][0] > 1:
        # Если пользователь возвращается из бана
        if 'Вернуться' in user_message:
            apologize(user_name)
            return "Возвращаемся к месту на котором остановились..."

        return False


@db_connection
def apologize(user_name, cursor=None):
    cursor.execute('''SELECT Employees.enable FROM Employees WHERE Employees.name = ?''', (user_name,))
    response = cursor.fetchall()
    if response[0][0] > 1:
        cursor.execute('''UPDATE Employees SET enable = ? WHERE name = ?;''', (response[0][0] - 1, user_name))
        if response[0][0] - 1 == 1:
            # Извинения приняты
            print('Извинения приняты')
            return True
        else:
            return False

    return False


@db_connection
def apologize(user_name, cursor=None):
    cursor.execute('''SELECT Employees.enable FROM Employees WHERE Employees.name = ?''', (user_name,))
    response = cursor.fetchall()
    if response[0][0] > 1:
        cursor.execute('''UPDATE Employees SET enable = ? WHERE name = ?;''', (response[0][0]-1, user_name))
        if response[0][0] - 1 == 1:
            # Извинения приняты
            print('Извинения приняты')
            return True
        else:
            return False

    return False

@db_connection
def check_position(user_name: str, position: list, cursor=None):
    cursor.execute('''SELECT Employees.position FROM Employees WHERE Employees.name = ?''', (user_name,))
    response = cursor.fetchall()
    if response[0][0] in position:
        return True
    else:
        return False

@db_connection
def add_token(user_name, employee_name, cursor=None):
    if check_position(user_name, ['admin', 'company']):
        employee_id = get_user_id(employee_name)
        if employee_id:
            token = generate_token()
            cursor.execute('''INSERT INTO Tokens (token,emp_id) VALUES (?,?)''', (token, employee_id))
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
    print_table(response, column_names)


@db_connection
def set_bot_state(user_name, new_state, bot, message, cursor=None):
    if new_state == 'Interviewer':
        bot.send_message(message.chat.id, AI_STATE_INTERVIEWER)
    elif new_state == 'Assistant':
        bot.send_message(message.chat.id, AI_STATE_ASSISTANT)
    elif new_state == 'Chat':
        bot.send_message(message.chat.id, AI_STATE_CHAT)

    cursor.execute('''UPDATE Employees SET bot_state = ? WHERE name = ?;''', (new_state, user_name))
    return None


@db_connection
def get_bot_state(user_name, cursor=None):
    cursor.execute('''SELECT Employees.bot_state FROM Employees WHERE name == ?;''', (user_name,))
    response = cursor.fetchall()
    return response[0][0]


@db_connection
def write_interview(interview_id, interview_list, cursor=None):
    interview_log = ''.join([message + '\n' for message in interview_list])
    cursor.execute(f'''UPDATE Tokens SET interview = ? WHERE id = ?;''', (interview_log, interview_id))


@db_connection
def finish_interview(interview_id, cursor=None):
    cursor.execute(f'''UPDATE Tokens SET title = 'Завершённое интервью', interview_enable = False WHERE id = ?''',
                   (interview_id,))


if __name__ == '__main__':
    init()
    select_all()
