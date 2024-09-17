# -*- coding: utf-8 -*-  # Языковая кодировка UTF-8
import json
import re

from nltk import word_tokenize
from rich.console import Console
from rich.table import Table
import pymorphy2

from tools.core.custom_punkt_tokenizer import sent_tokenize_with_abbr
from tools.core.utils import wait_for_enter_to_analyze
from tools.core.text_preparation import TextPreProcessor

morph = pymorphy2.MorphAnalyzer()

console = Console()


def get_pos(word):
    """
    Определяет часть речи для данного токена.

    :param word: str - Входной токен для определения части речи.

    :return: str - Часть речи слова (например, 'NOUN', 'VERB', 'ADJ' и т.д.) или кастомные
     варианты (например, 'NUMBER', 'LATIN_WORD', 'FULL_STOP').
    """
    if word.isdigit():  # Проверка на числовое значение
        return 'NUMBER'
    if re.match(r'[a-zA-Z]', word):  # Проверка на латинские буквы
        return 'LATIN_WORD'
    if re.match(r'[.]', word):  # Проверка на знак препинания
        return 'FULL_STOP'
    if re.match(r'[!]', word):  # Проверка на знак препинания
        return 'EXCLAMATION_MARK'
    if re.match(r'[?]', word):  # Проверка на знак препинания
        return 'QUESTION_MARK'
    if re.match(r'[,]', word):  # Проверка на знак препинания
        return 'COMMA'
    if re.match(r'[;]', word):  # Проверка на знак препинания
        return 'SEMICOLON'
    if re.match(r'[:]', word):  # Проверка на знак препинания
        return 'COLON'
    parsed = morph.parse(word)[0]
    return parsed.tag.POS


def extract_positions(text, show_analysis=True):
    """
    Извлекает позиции слов, их части речи на разных позициях предложении.

    :param text: str - Входной текст для анализа.
    :param show_analysis: Bool - Флаг для отображения анализа (по умолчанию True).

    :return: str - JSON-объект с токенами и их частями речи на разных позициях для каждого предложения.
    """
    text_processor = TextPreProcessor()
    sentences = sent_tokenize_with_abbr(text)

    token_positions_in_sent = []

    for i, sent in enumerate(sentences, start=1):
        sent = text_processor.process_text(sent)
        sent = re.sub(r'([.,!?;])', r' \1 ', sent)
        sent = re.sub(r'[^а-яА-ЯёЁA-Za-z0-9\s.,!?;]', '', sent)

        # Токенизация предложения

        tokens = word_tokenize(sent, language="russian")
        if len(tokens) < 5:
            continue

        positions = {
            'first': tokens[0],
            'second': tokens[1],
            'antepenultimate': tokens[-3],
            'penultimate': tokens[-2],
            'last': tokens[-1]
        }

        # Получаем часть речи для каждого токена
        positions_with_pos = {
            position: (token, get_pos(token))
            for position, token in positions.items()
        }

        token_positions_in_sent.append({'SENTENCE_NUMBER': i, 'positions': positions_with_pos})

    positions_contexts = json.dumps(token_positions_in_sent, ensure_ascii=False)
    if show_analysis:
        print_positions(positions_contexts)
    return positions_contexts


def print_positions(sentence_data):
    """
    Выводит позиционные контексты слов и их частей речи.

    :param sentence_data: str - JSON-строка с данными о позициях слов, их частях речи.
    """
    sentence_data = json.loads(sentence_data)

    table = Table()

    table.add_column("Sent", justify="center", style="bold", no_wrap=True, width=19)
    table.add_column("First", justify="center", no_wrap=True, width=25)
    table.add_column("Second", justify="center", no_wrap=True, width=25)
    table.add_column("Antepenultimate", justify="center", no_wrap=True, width=30)
    table.add_column("Penultimate", justify="center", no_wrap=True, width=25)
    table.add_column("Last", justify="center", no_wrap=True, width=25)

    for data in sentence_data:
        sentence_number = data['SENTENCE_NUMBER']
        positions = data['positions']

        tokens_row = [f"{sentence_number}"]
        pos_row = [""]  # Пустая ячейка для выравнивания под номером предложения

        for position in ['first', 'second', 'antepenultimate', 'penultimate', 'last']:
            token, pos = positions[position]
            tokens_row.append(token)
            pos_row.append(pos)

        # Добавляем строки в таблицу: первая строка — токены, вторая строка — части речи
        table.add_row(*tokens_row)
        table.add_row(*pos_row, end_section=True)  # Добавляем пустую строку после строки с частями речи

    console.print(table)
    wait_for_enter_to_analyze()


if __name__ == "__main__":
    # Текст для примера (сгенерирован ИИ)
    text = """
    Осенний ветер за окном напоминал о скором приходе холодов. Листья деревьев медленно кружились в воздухе, постепенно 
    покрывая землю золотым ковром. В парке гуляли немногочисленные прохожие, наслаждаясь последними тёплыми днями. Вдоль 
    аллеи бежала собака, радостно виляя хвостом. Маленький мальчик с интересом наблюдал за ней, крепко держа за руку свою 
    маму. Она говорила ему о том, как важно сохранять природу и уважать окружающий мир. Вдалеке был виден силуэт 
    человека, сидящего на лавочке с книгой. Он не спешил никуда, погружённый в чтение. Вокруг царила атмосфера 
    умиротворённости и спокойствия. Солнце постепенно уходило за горизонт, окутывая парк мягким оранжевым светом. Небо 
    меняло свой цвет, переходя от светло-голубого к насыщенному розовому. Птицы готовились к ночи, прячась в ветвях 
    деревьев. Где-то рядом слышался тихий плеск воды из фонтана. Люди начинали расходиться по домам, постепенно покидая 
    парк. И вот, когда город погрузился в вечерние сумерки, наступила долгожданная тишина.
    """

    sentence_data = extract_positions(text)
