import numpy as np
import pickle as pkl
from config import BIG_PARAGRAPH_THRESHOLD, SMALL_PARAGRAPH_THRESHOLD


def merge_small_paragraphs(paragraph_list: list):
    all_are_bigger_than_threshold = False
    cur_id = 0
    while not all_are_bigger_than_threshold:
        # Обработчик для 0
        if cur_id == 0:
            if len(paragraph_list[0]) < SMALL_PARAGRAPH_THRESHOLD:
                merged_paragraph = ''.join(paragraph_list[0] + paragraph_list[1])
                paragraph_list = [merged_paragraph] + paragraph_list[2:]
            else:
                cur_id += 1

        # Для всех остальных
        elif len(paragraph_list[cur_id]) < SMALL_PARAGRAPH_THRESHOLD:
            if len(paragraph_list[cur_id-1]) < len(paragraph_list[cur_id+1]):
                merged_paragraph = ''.join(paragraph_list[cur_id - 1] + paragraph_list[cur_id])
                paragraph_list = paragraph_list[:cur_id-1] + [merged_paragraph] + paragraph_list[cur_id + 1:]
                cur_id -= 1
            else:
                merged_paragraph = ''.join(paragraph_list[cur_id] + paragraph_list[cur_id + 1])
                paragraph_list = paragraph_list[:cur_id] + [merged_paragraph] + paragraph_list[cur_id + 2:]
        else:
            cur_id += 1
        if cur_id == len(paragraph_list)-1:
            all_are_bigger_than_threshold = True
    return paragraph_list


def split_big_paragraph(paragraph: str) -> list:
    # Проверка строки на её размер
    if len(paragraph) < BIG_PARAGRAPH_THRESHOLD:
        return [paragraph]

    spaces_count = 4
    res_list = []
    concat_str = ''
    continue_flag = False
    # Проходим по строкам в параграфе
    for string in paragraph.split('\n'):
        if len(string) == 0:
            continue

        # Если в строке мало пробелов, то считаем её преходящей
        if string.count(" ") < spaces_count:
            res_list.append(concat_str)
            concat_str = ''

        # Удаление лишних пробелов
        if string.count(' ') < len(string) // 2:
            if not continue_flag:
                string = string.strip(' ').strip('\t')
            else:
                continue_flag = False
        else:
            continue_flag = True

        concat_str = concat_str + string + '\n'

    # Записываем последний параграф
    res_list.append(concat_str)
    return res_list


def get_metrics(texts_list: list):
    av_len, max_len, min_len = 0, 0, 1000
    av_row, max_row, min_row = 0, 0, 1000
    for i, paragraph in enumerate(texts_list, 1):
        av_len += len(paragraph)
        av_row += paragraph.count('\n')
        if max_len < len(paragraph):
            max_len = len(paragraph)
        if min_len > len(paragraph):
            min_len = len(paragraph)
        if max_row < paragraph.count('\n'):
            max_row = paragraph.count('\n')
        if min_row > paragraph.count('\n'):
            min_row = paragraph.count('\n')

    print(f'Average len:{int(av_len / i)}, Max len:{max_len}, Min len:{min_len}')
    print(f'Average rows:{int(av_row / i)}, Max rows:{max_row}, Min rows:{min_row}')


def text_preprocess(paragraph_list: list):
    paragraph_list_copy = paragraph_list.copy()
    paragraph_id = 0
    paragraph_id_loc = 0
    while paragraph_id < len(paragraph_list):

        paragraph_list_copy[paragraph_id_loc] = paragraph_list[paragraph_id].strip('\n')
        splited_paragraph = split_big_paragraph(paragraph_list_copy[paragraph_id_loc])
        paragraph_list_copy = paragraph_list_copy[:paragraph_id_loc] + splited_paragraph + \
                              paragraph_list_copy[paragraph_id_loc + 1:]
        paragraph_id_loc += len(splited_paragraph)
        paragraph_id += 1

    paragraph_list_copy = [paragraph.strip('\n') + '\n' for paragraph in paragraph_list_copy if len(paragraph) > 0]
    paragraph_list_copy = merge_small_paragraphs(paragraph_list_copy)[:-1]
    paragraph_list_copy = [paragraph + '\n' for paragraph in paragraph_list_copy]
    return paragraph_list_copy


def chair_data(full_text: str) -> list:
    paragraph_list = full_text.split('\n\n')
    texts_list = text_preprocess(paragraph_list)
    get_metrics(texts_list)
    return texts_list


if __name__ == '__main__':
    filename = 'TOE'
    with open(f'../chairs_data/{filename}.txt', 'r', encoding='UTF-8') as file:
        text = file.read().lower()
    with open(f'../chairs_data/{filename}_for_LLM.pkl', 'wb') as file:
        pkl.dump(text,file)
