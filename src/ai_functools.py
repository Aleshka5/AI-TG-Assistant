def get_base_guestions(n = 5) -> list:
    return ['Первый вопрос','Второй вопрос','Третий вопрос','Четвёртый вопрос','Пятый вопрос']

def get_addition_question(previous_answer : str = '') -> str:
    print(previous_answer)
    return f'Дополнительный вопрос от нейросети по ответу: {previous_answer}'

def just_chat(input_question : str = '') -> str:
    return ''