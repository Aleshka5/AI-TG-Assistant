import os
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


def get_similar_texts(texts: list, embeddings: list, phrase: str) -> list:
    input_tensor = tf.convert_to_tensor([phrase,], dtype=tf.string)
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


def texts2embeddings(texts: list, file_name: str) -> list:
    delete_list = [',',':','"','-',';','(',')','т.п.','\n']

    texts = np.array([(' '.join(text.split())).replace('"', '').replace('-', '').replace(',', '').replace(';','')
                     .replace(':', '').replace('(', '').replace(')', '').replace('т.п.', '').replace('\n', '')
                      for text in texts])
    elmo = load_embedder()
    embeddings_list = []
    for text in texts:
        input_tensor = tf.convert_to_tensor([text,], dtype=tf.string)
        # Создание векторов тестов
        embedding = elmo(input_tensor)
        embeddings_list.append(embedding)

    with open(f'./chairs_data/{file_name}_embeddings.pkl','wb') as file:
        pkl.dump(embeddings_list,file)


def get_embeddings(filename: str, texts: list):
    if not os.path.exists(f'./chairs_data/{filename}_embeddings.pkl'):
        print('Not founded')
        texts2embeddings(texts, filename)

    with open(f'./chairs_data/{filename}_embeddings.pkl', 'rb') as file:
        embeddings = pkl.load(file)

    return embeddings


def just_chat(input_question : str, chair_name: str) -> str:
    file_name = chair_name
    with open(f'./chairs_data/{file_name}.txt', 'r', encoding='UTF-8') as file:
        text = file.read().lower()
    # Предобработка данных кафедры
    texts = chair_data(text)
    # Преобразование/Считываение данных кафедр в векторы
    embeddings = get_embeddings(file_name, texts)
    # Получение наиболее нужных текстов по кафедре
    top_texts = get_similar_texts(texts, embeddings, input_question)
    return top_texts[0]


if __name__ == '__main__':
    file_name = 'Design'
    with open(f'./chairs_data/{file_name}.txt', 'r', encoding='UTF-8') as file:
        text = file.read().lower()
    # Предобработка данных кафедры
    texts = chair_data(text)
    # Преобразование/Считываение данных кафедр в векторы
    embeddings = get_embeddings(file_name,texts)
    # Получение наиболее нужных текстов по кафедре
    top_texts = get_similar_texts(texts, embeddings, 'Выпускники устраиваются на работу.')
    print(top_texts)