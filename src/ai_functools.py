import os
import openai
import tensorflow as tf
import pickle as pkl
import numpy as np
import tensorflow_hub as hub
from tensorflow.keras.metrics import CosineSimilarity
from functools import cache
from src.parsers import chair_data


@cache
def load_embedder():
    return hub.KerasLayer("http://files.deeppavlov.ai/deeppavlov_data/elmo_ru-wiki_600k_steps.tar.gz", trainable=False)


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
    # print(np.array(list_similarity)[range_ingexes])
    # print(np.array(texts)[range_ingexes])
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
    with open(f'./chairs_data/{file_name}_edited.txt', 'w', encoding='UTF-8') as file:
        file.write(''.join(texts))
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
        answer = str(__insert_newlines(completion.choices[0].message.content))
        print(answer)
        return answer

    except Exception as ex:
        print(ex)
        print('Проверьте доступ к API либо подождите, возможно сейчас модель перегружена запросами.')
        return "Error: Проверьте доступ к API либо подождите, возможно сейчас модель перегружена запросами."


if __name__ == '__main__':
    # file_name = 'Design'
    # with open(f'../chairs_data/{file_name}.txt', 'r', encoding='UTF-8') as file:
    #     text = file.read().lower()
    # # Предобработка данных кафедры
    # texts = chair_data(text)
    # # Преобразование/Считываение данных кафедр в векторы
    # embeddings = get_embeddings(file_name,texts)
    # # Получение наиболее нужных текстов по кафедре
    # top_texts = get_similar_texts(texts, embeddings, 'Выпускники устраиваются на работу.')
    # print(top_texts)

    just_chat('Расскажи мне, как лучше развивать персонал на кафедре ВМСС?')
