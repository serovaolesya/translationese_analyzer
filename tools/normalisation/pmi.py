# -*- coding: utf-8 -*- # Языковая кодировка UTF-8
import os
import glob
import math
import re
from collections import Counter

from colorama import Style, Fore
from nltk import word_tokenize
from rich.table import Table
from rich.console import Console

from tools.core.custom_punkt_tokenizer import sent_tokenize_with_abbr
from tools.core.lemmatizators import lemmatize_words, lemmatize_words_into_sents_for_pmi
from tools.core.utils import wait_for_enter_to_analyze

console = Console()


def process_text_for_pmi_wordforms(text):
    """
    Разбивает текст на предложения, токенизирует их, и возвращает список предложений,
    где каждое предложение представлено списком токенов без знаков препинания и некириллических букв,
    лемматизация пока что отсутствует.

    :param text: Текст для обработки.
    :return: Список предложений, где каждое предложение представлено списком токенов.
    """
    # Очистка текста от лишних символов, кроме знаков препинания и кириллических букв
    text = re.sub(r'[^а-яА-ЯёЁ\s\.\!\?\-]', '', text.lower())

    sentences = sent_tokenize_with_abbr(text)
    wait_for_enter_to_analyze()

    # Токенизация предложений
    tokenized_sentences = []
    for sentence in sentences:
        tokens = word_tokenize(sentence, language="russian")
        # Фильтруем токены, оставляя только кириллические буквы и пропуская знаки препинания
        filtered_tokens = [token for token in tokens if token not in ['.', '?', '!']]
        tokenized_sentences.append(filtered_tokens)
    wait_for_enter_to_analyze()

    return tokenized_sentences


def read_texts_from_directory(directory):
    """
    Считывает все текстовые файлы из указанной директории и возвращает их содержимое в виде списка строк.

    :param directory: Путь к директории, содержащей текстовые файлы.
    :return: Множество строк, каждая из которых представляет содержимое одного текстового файла.
    """
    corpus = set()
    # Ищем все файлы с расширением .txt в указанной директории
    for filename in glob.glob(os.path.join(directory, '*.txt')):
        with open(filename, 'r', encoding='utf-8') as file:
            text = file.read()
            corpus.add(text)
    return corpus


def calculate_pmi(corpus_directory=None, corpus_set=None):
    """
    Расчет PMI для корпуса текстов из указанной директории.

    :param corpus_directory: Путь к директории, содержащей текстовые файлы, если используется директория.
    :param corpus_set: Множество строк, представляющих собой тексты, если используется набор текстов.
    :return: Словарь биграмм и их значений PMI, отсортированный по убыванию PMI, число биграммов > 0,
    """
    if corpus_directory:
        corpus = read_texts_from_directory(corpus_directory)
    else:
        corpus = corpus_set
    all_bigrams = Counter()
    word_counts = Counter()
    total_bigrams_above_zero = 0
    total_bigrams_count = 0

    # Обработка каждого текста в корпусе
    for text in corpus:
        # Лемматизация текста и получение полной информации по каждому слову
        lemmatized_sentences = lemmatize_words_into_sents_for_pmi(text)

        for sentence in lemmatized_sentences:
            word_counts.update(sentence)

            # Создание биграмм внутри предложения
            bigrams = zip(sentence[:-1], sentence[1:])
            all_bigrams.update(bigrams)  # Обновляем частоты биграмм

    total_word_number = sum(word_counts.values())

    # Вычисляем вероятности для слов и биграмм
    p_word = {word: count / total_word_number for word, count in word_counts.items()}
    p_bigram = {bigram: count / total_word_number for bigram, count in all_bigrams.items()}

    pmi_values = {}

    for bigram, count in all_bigrams.items():
        w1, w2 = bigram
        pmi = math.log2(p_bigram[bigram] / (p_word[w1] * p_word[w2]))
        if pmi > 0:
            pmi_values[bigram] = pmi
            total_bigrams_above_zero += 1  # Увеличиваем счетчик биграммов с положительным PMI
        total_bigrams_count += 1  # Увеличиваем общий счётчик биграммов

    normalized_bigrams_above_zero = total_bigrams_above_zero / total_bigrams_count if total_bigrams_count > 0 else 0

    sorted_pmi_values = sorted(pmi_values.items(), key=lambda x: x[1], reverse=True)
    return dict(sorted_pmi_values), total_bigrams_above_zero, normalized_bigrams_above_zero


def display_pmi_table(pmi_values):
    """
    Выводит таблицу биграммов с PMI выше заданного минимального значения.

    :param pmi_values: Словарь биграмм и их значений PMI.
    """
    while True:
        try:
            min_pmi_input = input(
                Fore.LIGHTGREEN_EX + Style.BRIGHT + f"Введите минимальное значение интересующего Вас PMI или просто нажмите 'Enter', "
                                                    f"\nчтобы продолжить (по умолчанию значение=0): \n").strip()

            if not min_pmi_input:
                min_pmi = 0.0
                break
            else:
                min_pmi = float(min_pmi_input)
                break
        except ValueError:
            print(Fore.LIGHTRED_EX + Style.BRIGHT + "\nОшибка! Введите числовое значение.")

    print(
        Fore.LIGHTYELLOW_EX + Style.BRIGHT + f"\n             БИГРАММЫ И ИХ ЗНАЧЕНИЯ PMI" + Fore.RESET)
    table = Table()
    table.add_column("№", justify="center")
    table.add_column("Биграмма", justify="center")
    table.add_column("PMI", justify="center")

    # Фильтруем и сортируем биграммы по PMI, выводим только те, что больше min_pmi
    filtered_bigrams = {bigram: pmi for bigram, pmi in pmi_values.items() if pmi > min_pmi}
    sorted_bigrams = sorted(filtered_bigrams.items(), key=lambda x: x[1], reverse=True)

    for index, (bigram, pmi) in enumerate(sorted_bigrams, start=1):
        table.add_row(str(index), f"{bigram[0]} {bigram[1]}", f"{pmi:.4f}")

    console.print(table)

    print(Fore.LIGHTYELLOW_EX + Style.BRIGHT + f"Найдено {len(filtered_bigrams)} биграммов с PMI > {min_pmi}.\n")

if __name__ == "__main__":

    # Пример того, как передавать директорию с Вашими текстами в метод calculate_pmi. Раскомментируйте код ниже.
    # directory = '../your_directory'  # (должна быть в головной директории)
    # example_1 = calculate_pmi(corpus_directory=directory)
    # display_pmi_table(example_1)


    # Список текстов для примера (сгенерированы ИИ)
    text_1 = """
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

    text_2 = """
    Космонавт Алексей всегда мечтал о звёздах. С детства он читал книги о космосе и представлял себя на 
    борту космического корабля. После долгих лет учёбы и тренировок, его мечта стала реальностью. В 2024 году Алексей 
    был выбран для участия в международной миссии на Марс. Экипаж состоял из учёных и инженеров разных стран, 
    и все они работали как единое целое. Путешествие длилось шесть месяцев, и каждый день приносил новые вызовы. На 
    борту Алексей отвечал за поддержание систем жизнеобеспечения. Технологии, используемые в полёте, 
    были новаторскими и требовали постоянного контроля. В свободное время он смотрел в иллюминатор на бесконечный 
    космос, размышляя о своём месте во Вселенной. По прибытию на Марс, команда начала исследования поверхности 
    планеты. Алексей был первым человеком, ступившим на красную пыль марсианской пустыни. Он взял пробы грунта и 
    отправил их на анализ в корабль. Возвращение на Землю прошло успешно, и Алексей стал национальным героем. Его 
    истории вдохновляли новое поколение детей мечтать о космосе. Алексей продолжил работать в космической программе, 
    передавая свой опыт молодым космонавтам. В каждом его слове чувствовалась страсть к исследованиям и вера в 
    будущее человечества среди звёзд.
    """

    texts_set = set()

    # Добавляем тексты в set
    texts_set.update([text_1, text_2])

    example_2, count_above_zero, normalized_bigrams_above_zero = calculate_pmi(corpus_set=texts_set)
    display_pmi_table(example_2)
    print(normalized_bigrams_above_zero)