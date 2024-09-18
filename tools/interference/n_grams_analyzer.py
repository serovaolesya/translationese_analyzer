# -*- coding: utf-8 -*- # Языковая кодировка UTF-8
import json
import re
from collections import Counter

import pymorphy2
from colorama import Style, Fore
from nltk import ngrams
from rich.console import Console
from rich.table import Table

from tools.core.utils import display_grammemes, wait_for_enter_to_analyze
from tools.core.lemmatizators import lemmatize_words_into_sents_for_n_grams
from tools.core.text_preparation import TextPreProcessor

morph = pymorphy2.MorphAnalyzer()

console = Console()


def pos_ngrams(text, n_values=(1, 2, 3), show_analysis=True):
    """
    Вычисляет n-граммы частей речи для русского текста и возвращает результаты в виде строк JSON.

    :param text: Входной текст на русском языке.
    :param n_values: Размеры n-грамм, которые нужно вычислить (по умолчанию (1, 2, 3)).
    :param show_analysis: Флаг для отображения анализа (по умолчанию True).

    :return tuple: Строки JSON с абсолютными и нормализованными частотами униграммов, биграммов и триграммов.
    """
    if show_analysis:
        display_grammemes()
        wait_for_enter_to_analyze()
        print(Fore.LIGHTYELLOW_EX + Style.BRIGHT + "\n                    ЧАСТОТЫ ЧАСТЕРЕЧНЫХ N-ГРАММОВ" + Fore.RESET)
        print(Fore.LIGHTBLUE_EX + "По умолчанию в консоль выводятся n-граммы с абсолютной частотой >20." + Fore.RESET)

    text_processor = TextPreProcessor()
    text = text_processor.process_text(text)
    n_grams, lemmas = lemmatize_words_into_sents_for_n_grams(text)

    unigram_counts = Counter()
    bigram_counts = Counter()
    trigram_counts = Counter()

    for n in n_values:
        if n == 1:
            unigrams = list(ngrams(n_grams, n))
            unigram_counts.update(unigrams)
        elif n == 2:
            bigrams = list(ngrams(n_grams, n))
            bigram_counts.update(bigrams)
        elif n == 3:
            trigrams = list(ngrams(n_grams, n))
            trigram_counts.update(trigrams)

    def normalize_frequencies(counts, n):
        total_ngrams = sum(counts.values())
        return {ngram: round((count / total_ngrams) * 100, 3) for ngram, count in counts.items()}

    unigram_normalized_frequencies = normalize_frequencies(unigram_counts, 1)
    bigram_normalized_frequencies = normalize_frequencies(bigram_counts, 2)
    trigram_normalized_frequencies = normalize_frequencies(trigram_counts, 3)

    def convert_keys_to_strings(counter):
        return {str(k): v for k, v in counter.items()}

    def sort_counter_by_value(counter):
        return dict(sorted(counter.items(), key=lambda item: item[1], reverse=True))

    unigram_counts = json.dumps(convert_keys_to_strings(sort_counter_by_value(unigram_counts)), ensure_ascii=False)
    unigram_normalized_frequencies = json.dumps(convert_keys_to_strings(sort_counter_by_value(unigram_normalized_frequencies)),
                       ensure_ascii=False)
    bigram_counts = json.dumps(convert_keys_to_strings(sort_counter_by_value(bigram_counts)), ensure_ascii=False)
    bigram_normalized_frequencies = json.dumps(convert_keys_to_strings(sort_counter_by_value(bigram_normalized_frequencies)),
                       ensure_ascii=False)
    trigram_counts = json.dumps(convert_keys_to_strings(sort_counter_by_value(trigram_counts)), ensure_ascii=False)
    trigram_normalized_frequencies = json.dumps(convert_keys_to_strings(sort_counter_by_value(trigram_normalized_frequencies)),
                       ensure_ascii=False)
    if show_analysis:
        display_ngrams_summary(unigram_counts, unigram_normalized_frequencies, bigram_counts,
                               bigram_normalized_frequencies, trigram_counts, trigram_normalized_frequencies)
    return unigram_counts, unigram_normalized_frequencies, bigram_counts, bigram_normalized_frequencies, trigram_counts, trigram_normalized_frequencies


def character_ngrams(text, n_values=(1, 2, 3), show_analysis=True):
    """
    Вычисляет символьные n-граммы для текста и возвращает результаты в виде строк JSON.

    :param text: Входной текст.
    :param n_values: Размеры n-грамм, которые нужно вычислить (по умолчанию (1, 2, 3)).
    :param show_analysis: Флаг для отображения анализа (по умолчанию True).

    :return tuple: Строки JSON с абсолютными и нормализованными частотами униграммов, биграммов и триграммов.
    """
    if show_analysis:
        print(Fore.LIGHTYELLOW_EX + Style.BRIGHT + "\n                      ЧАСТОТЫ БУКВЕННЫХ N-ГРАММОВ" + Fore.RESET)
        print(
            Fore.LIGHTRED_EX + Style.BRIGHT + "Внимание! N-граммы '<' и '>' используются для обозначания начала и конца \nслов соответственно.\n" + Fore.RESET)
        wait_for_enter_to_analyze()
    # Удаление всех знаков препинания и лишних символов, оставляя только буквы и пробелы
    text = re.sub(r'[^а-яА-ЯёЁ\s]', '', text)

    text = text.lower()

    # Разделение текста на слова и добавление специальных токенов начала и конца слова
    words = text.split()
    processed_words = ['<' + word + '>' for word in words]

    # Объединение всех слов в строку
    processed_text = ''.join(processed_words)

    unigram_counts = Counter()
    bigram_counts = Counter()
    trigram_counts = Counter()
    unigram_normalized_frequencies = {}
    bigram_normalized_frequencies = {}
    trigram_normalized_frequencies = {}

    total_letters = sum(1 for char in processed_text if char)

    # Генерация и подсчет n-грамм
    for n in n_values:
        ngram_counts = Counter()
        char_ngrams = list(ngrams(processed_text, n))
        ngram_counts.update(char_ngrams)

        normalized_frequencies = {}
        for ngram in ngram_counts:
            all_n_grams = total_letters - n + 1
            normalized_frequencies[ngram] = round((ngram_counts[ngram] / all_n_grams) * 100, 3)

        if n == 1:
            unigram_counts = ngram_counts
            unigram_normalized_frequencies = normalized_frequencies
        elif n == 2:
            bigram_counts = ngram_counts
            bigram_normalized_frequencies = normalized_frequencies
        elif n == 3:
            trigram_counts = ngram_counts
            trigram_normalized_frequencies = normalized_frequencies

    # Преобразование ключей-кортежей в строки для JSON
    def convert_keys_to_strings(counter):
        return {str(k): v for k, v in counter.items()}

    def sort_counter_by_value(counter):
        return dict(sorted(counter.items(), key=lambda item: item[1], reverse=True))

    unigram_counts = json.dumps(convert_keys_to_strings(sort_counter_by_value(unigram_counts)), ensure_ascii=False)
    unigram_normalized_frequencies = json.dumps(convert_keys_to_strings(sort_counter_by_value(unigram_normalized_frequencies)),
                       ensure_ascii=False)
    bigram_counts = json.dumps(convert_keys_to_strings(sort_counter_by_value(bigram_counts)), ensure_ascii=False)
    bigram_normalized_frequencies = json.dumps(convert_keys_to_strings(sort_counter_by_value(bigram_normalized_frequencies)),
                       ensure_ascii=False)
    trigram_counts = json.dumps(convert_keys_to_strings(sort_counter_by_value(trigram_counts)), ensure_ascii=False)
    trigram_normalized_frequencies = json.dumps(convert_keys_to_strings(sort_counter_by_value(trigram_normalized_frequencies)),
                       ensure_ascii=False)
    if show_analysis:
        display_ngrams_summary(unigram_counts, unigram_normalized_frequencies, bigram_counts,
                               bigram_normalized_frequencies, trigram_counts, trigram_normalized_frequencies)
    return unigram_counts, unigram_normalized_frequencies, bigram_counts, bigram_normalized_frequencies, trigram_counts, trigram_normalized_frequencies


def display_ngrams(title, ngram_counts, normalized_counts, min_frequency=20):
    """
    Отображает таблицы с частотами n-грамм, фильтруя по минимальной частоте.

    :param title: Заголовок таблицы.
    :param ngram_counts: JSON-строка с абсолютными частотами n-граммов.
    :param normalized_counts: JSON-строка с нормализованными частотами n-граммов.
    :param min_frequency: Минимальная частота для отображения (по умолчанию 20).
    """
    ngram_counts = json.loads(ngram_counts)
    normalized_counts = json.loads(normalized_counts)
    print(Fore.LIGHTYELLOW_EX + Style.BRIGHT + f"                          {title.upper()}" + Fore.RESET)
    wait_for_enter_to_analyze()
    table = Table()

    table.add_column("N-грамм\n", justify="center", no_wrap=True)
    table.add_column("Абсолютная частота\n", justify="center")
    table.add_column("Нормализованная частота \n(%)", justify="center")

    for ngram, count in ngram_counts.items():
        if count >= min_frequency:
            normalized_freq = normalized_counts.get(ngram, 0)
            table.add_row(ngram, str(count), str(normalized_freq) + "%")

    if len(table.rows) > 0:
        console.print(table)
        wait_for_enter_to_analyze()
    else:
        print(Fore.LIGHTRED_EX + f"Отсутствуют {title.lower()} n-граммы с частотой > или = {min_frequency}." + Fore.RESET)
        wait_for_enter_to_analyze()


def display_ngrams_summary(unigram_counts, unigram_freq, bigram_counts, bigram_freq, trigram_counts, trigram_freq):
    """
    Запрашивает минимальную частоту и отображает результаты для униграммов, биграммов и триграммов.

    :param unigram_counts: JSON-строка с абсолютными частотами униграммов.
    :param unigram_freq: JSON-строка с нормализованными частотами униграммов.
    :param bigram_counts: JSON-строка с абсолютными частотами биграммов.
    :param bigram_freq: JSON-строка с нормализованными частотами биграммов.
    :param trigram_counts: JSON-строка с абсолютными частотами триграммов.
    :param trigram_freq: JSON-строка с нормализованными частотами триграммов.
    """
    print(
        Fore.LIGHTGREEN_EX + Style.BRIGHT + "Введите интересующую Вас минимальную частоту n-граммов или просто нажмите "
                                            "'Enter' \n(по умолчанию значение=20):" + Fore.RESET)
    while True:
        min_frequency = input()
        if not min_frequency:
            min_frequency = 20
            break
        try:
            min_frequency = int(min_frequency)
            if min_frequency > 0:
                break
            else:
                print(Fore.LIGHTRED_EX + "Ошибка: Введите значение больше нуля.\n" + Fore.RESET)
        except ValueError:
            print(Fore.LIGHTRED_EX + "Ошибка: Введите числовое значение или нажмите 'Enter'.\n" + Fore.RESET)
    display_ngrams("Униграммы", unigram_counts, unigram_freq, min_frequency)
    display_ngrams("Биграммы", bigram_counts, bigram_freq, min_frequency)
    display_ngrams("Триграммы", trigram_counts, trigram_freq, min_frequency)


if __name__ == "__main__":
    # Текст для примера (сгенерирован ИИ)
    text = """
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
    unigram_counts, unigram_normalized_frequencies, bigram_counts, bigram_normalized_frequencies, trigram_counts, trigram_normalized_frequencies = character_ngrams(
        text)

    unigram_counts, unigram_normalized_frequencies, bigram_counts, bigram_normalized_frequencies, trigram_counts, trigram_normalized_frequencies = pos_ngrams(
        text)
