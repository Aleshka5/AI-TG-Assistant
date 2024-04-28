import os
import openai
from src import db
import tensorflow as tf
import pickle as pkl
import numpy as np
import tensorflow_hub as hub
from tensorflow.keras.metrics import CosineSimilarity
from functools import cache
from src.tools import get_chairs_list
from src.parsers import chair_data

@cache
def load_embedder():
    elmo = hub.KerasLayer("http://files.deeppavlov.ai/deeppavlov_data/elmo_ru-wiki_600k_steps.tar.gz", trainable=False)
    # elmo = hub.KerasLayer("C:/Users/Aleshka5/Desktop/Git_repos/AI-TG-Assistant/model", trainable=False)
    return elmo


def __get_similar_texts(texts: list, embeddings: list, phrase: str) -> list:
    input_tensor = tf.convert_to_tensor([phrase, ], dtype=tf.string)
    elmo = load_embedder()
    # Создание вектора переданного ответа
    phrase_embedding = elmo(input_tensor)

    list_similarity = []
    for embedding in embeddings:
        similarity = CosineSimilarity()(phrase_embedding, embedding)
        list_similarity.append(similarity)

    range_ingexes = np.argsort(list_similarity)[::-1]
    return np.array(texts)[range_ingexes][:3]


def __texts2embeddings(texts: list) -> list:
    delete_list = [',', ':', '"', '-', ';', '(', ')', 'т.п.', '\n', '/']

    for text_id in range(len(texts)):
        text = texts[text_id]

        for symbol in delete_list:
            text = text.replace(symbol, ' ')

        text = ''.join(text.split())
        texts[text_id] = text

    texts = np.array(texts)
    # texts = np.array([(' '.join(text.split())).replace('"', '').replace('-', '').replace(',', '').replace(';','')
    #                  .replace(':', '').replace('(', '').replace(')', '').replace('т.п.', '').replace('\n', '')
    #                   for text in texts])

    elmo = load_embedder()
    embeddings_list = []

    for text in texts:
        input_tensor = tf.convert_to_tensor([text, ], dtype=tf.string)
        # Создание векторов тестов
        embedding = elmo(input_tensor)
        embeddings_list.append(embedding)

    return embeddings_list


def __get_embeddings(filename: str, texts: list):
    if not os.path.exists(f'./chairs_data/{filename}_embeddings.pkl'):

        embeddings = __texts2embeddings(texts)
        with open(f'./chairs_data/{filename}_embeddings.pkl', 'wb') as file:
            pkl.dump(embeddings, file)

    else:
        with open(f'./chairs_data/{filename}_embeddings.pkl', 'rb') as file:
            embeddings = pkl.load(file)

    return embeddings


def get_similar_texts(input_question: str, chair_name: str) -> str:
    file_name = chair_name
    with open(f'./chairs_data/{file_name}.txt', 'r', encoding='UTF-8') as file:
        text = file.read().lower()
    # Предобработка данных кафедры
    texts = chair_data(text)
    # with open(f'./chairs_data/{file_name}_edited.txt', 'w', encoding='UTF-8') as file:
    #     file.write(''.join(texts))
    # Преобразование/Считываение данных кафедр в векторы
    embeddings = __get_embeddings(file_name, texts)
    # Получение наиболее нужных текстов по кафедре
    top_texts = __get_similar_texts(texts, embeddings, input_question)
    return top_texts[:3]


def __insert_newlines(text: str, max_len: int = 170) -> str:
    words = text.split()
    lines = []
    current_line = ""
    for word in words:
        if len(current_line + " " + word) > max_len:
            lines.append(current_line)
            current_line = ""
        current_line += " " + word
    lines.append(current_line)
    return "\n".join(lines)


def just_chat(topic: str, token: str, temp: int = 0.3) -> str:
    openai.api_key = token

    messages = [
        {"role": "system", "content": """Ты рускоязычный эксперт по системе оценивания образовательных организаций EFQM.
European Foundation for Quality Management - это организация, устанавливающая стандарты и методы для оценки качества и 
управления в организациях различных секторов, включая образование. EFQM Excellence Model основан на концепции 
непрерывного улучшения и включает в себя несколько критериев качества, которые охватывают все аспекты деятельности 
организации: Лидерство, Политика и стратегия, Люди, Партнерство и ресурсы, Процессы, продукты и услуги, 
Результаты клиентов, Результаты персонала, Общественные результаты, Результаты ключевых показателей. 
Отвечай только на вопросы связанные с образованием, образовательными организациями и косвенно связанные с сисетмой
EFQM и Excellence Model. Если вопрос не по теме ответь вежливым отказом."""},
        {"role": "user", "content": topic}
    ]

    try:
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=temp
        )
        answer = str(completion.choices[0].message.content)
        print(answer)
        return answer

    except Exception as ex:
        print(ex)
        print('Проверьте доступ к API либо подождите, возможно сейчас модель перегружена запросами.')
        return "Error: Проверьте доступ к API либо подождите, возможно сейчас модель перегружена запросами."

def gpt_analize(context: str, topic: str, token: str, temp: int = 0.3) -> str:
    openai.api_key = token

    messages = [
        {"role": "system", "content": f"""Вы оцениваете правдоподобность утверждения на основе предоставленных отрывков текста:
{context}При оценке правдоподобия утверждения учитывайте согласованность информации, представленной в текстах.
Ваш ответ должен отражать степень вероятности или правдоподобия утверждения, основываясь на анализе текстов."""},
        {"role": "user", "content": f"""Утверждение: {topic}\nОцени правдоподобность утверждения по шкале от 1 до 10 и
дай небольшой комментарий."""},
    ]

    print(messages[0]['content'])
    print(messages[1]['content'])
    try:
        # completion = openai.ChatCompletion.create(
        #     model="gpt-3.5-turbo",
        #     messages=messages,
        #     temperature=temp
        # )
        # answer = str(completion.choices[0].message.content)
        answer = 'Да, это верно на 10 баллов.'
        print(answer)
        return answer

    except Exception as ex:
        print(ex)
        print('Проверьте доступ к API либо подождите, возможно сейчас модель перегружена запросами.')
        return "Error: Проверьте доступ к API либо подождите, возможно сейчас модель перегружена запросами."

def ai_analize(interview_id: str, interview_log: str, chair_name: str, token: str):
    interview_list = interview_log.split('\n')
    print('int_list ',interview_list)
    question_id = 0
    summary = ''
    for answer in interview_list:
        context = ''
        if 'Вопрос' in answer:
            question_id = int(answer.split(':')[0][7:])
            continue

        if len(answer) <= 0:
            continue

        answer = answer[6:]
        print('answer', answer)

        if chair_name in get_chairs_list():
            top_texts = get_similar_texts(answer, chair_name)

        else:
            top_texts = get_similar_texts(answer, get_chairs_list()[0])

        for i, text in enumerate(top_texts,1):
            context.join(f'Текст {str(i)}: '+text+'\n')

        print('context ', context)
        summary += f'Анализ по вопросу {question_id}: ' + gpt_analize(context, answer, token) + '\n'

    print(len(summary))
    if len(summary) < 10000:
        db.write_analyze(interview_id, summary)


if __name__ == '__main__':
    file_name = 'Design'
    # with open(f'../chairs_data/{file_name}.txt', 'r', encoding='UTF-8') as file:
    #     text = file.read().lower()
    # # Предобработка данных кафедры
    # texts = chair_data(text)
    # Преобразование/Считываение данных кафедр в векторы
    # embeddings = get_embeddings(file_name,texts)
    # Получение наиболее нужных текстов по кафедре
    top_texts = get_similar_texts('Выпускники устраиваются на работу.', file_name)
    print(top_texts)

    # just_chat('Расскажи мне, как лучше развивать персонал на кафедре ВМСС?')
