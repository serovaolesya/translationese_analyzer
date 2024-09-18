# -*- coding: utf-8 -*- # Языковая кодировка UTF-8
import json
import re
from collections import defaultdict, Counter

import pymorphy2
from colorama import Fore, Style
from nltk.corpus import stopwords
from rich.console import Console
from rich.table import Table

from tools.core.custom_punkt_tokenizer import sent_tokenize_with_abbr
from tools.core.data import pronouns, prepositions, particles, conjunctions
from tools.core.utils import wait_for_enter_to_analyze
from tools.core.text_preparation import TextPreProcessor

console = Console()

# Загрузка стоп-слов
nltk_stopwords_ru = stopwords.words("russian")

# 1. Объединение всех списков в один
all_stopwords = set(conjunctions.conjunctions_list + prepositions.prepositions_list
                    + particles.particles_list + pronouns.pronouns_list + nltk_stopwords_ru)

# 2. Сортировка по длине по убыванию
all_stopwords_sorted = sorted(list(all_stopwords), key=len, reverse=True)

# Инициализация морфологического анализатора
morph = pymorphy2.MorphAnalyzer()


def get_pos(word):
    """
    Определяет часть речи для данного слова с использованием pymorphy2 + есть кастомные POS теги.

    Параметры:
    word (str): Слово для определения части речи.

    Возвращает:
    str: Часть речи (POS).
    """
    if word.isdigit():
        return 'NUMBER'
    if re.match(r'[a-zA-Z]', word):
        return 'LATIN'
    if re.match(r'[.!?]', word):
        return 'FINAL_PUNCT'
    if re.match(r'[,]', word):
        return 'COMMA'
    if re.match(r'[;]', word):
        return 'SEMICOLON'
    if re.match(r'[:]', word):
        return 'COLON'
    if re.match(r'[–]', word):
        return 'DASH'
    parsed = morph.parse(word)[0]
    return parsed.tag.POS


def contextual_function_words_in_trigrams(text, show_analysis=True):
    """
    Анализирует текст и находит триграммы, содержащие функциональные слова, а также их контексты и частоты.

    :param text (str): Входной текст для анализа.
    :param show_analysis (bool): Если True, выводит результаты анализа.

    :return tuple: Состоящий из трех JSON-строк:
        - Нормализованные частоты триграмм с функциональными словами.
        - Абсолютные частоты триграмм с функциональными словами.
        - Контексты триграмм с функциональными словами.
    """
    if show_analysis:
        print(
            Fore.LIGHTYELLOW_EX + Style.BRIGHT + "\n           ЧАСТОТЫ ЧАСТЕРЕЧНЫХ ТРИГРАММОВ С ФУНКЦИОНАЛЬНЫМИ СЛОВАМИ" + Fore.RESET)
        print(Fore.LIGHTRED_EX + Style.BRIGHT + "Внимание! В зависимости от размера текста подсчет может занять какое-то время. \nПожалуйста, будьте готовы подождать.\n" + Fore.RESET)
        wait_for_enter_to_analyze()
    text_processor = TextPreProcessor()
    sentences = sent_tokenize_with_abbr(text)

    func_words_contexts_with_tokens_or_pos = defaultdict(list)
    token_trigram_counts = Counter()
    pos_trigram_counts = {
        'one_function_word': Counter(),
        'two_function_words': Counter(),
        'three_function_words': Counter()
    }
    all_trigram_counts = Counter()

    for sent in sentences:
        # Предварительная обработка текста
        sent = text_processor.process_text(sent)
        # Разделение слов и знаков препинания пробелами
        sent = re.sub(r'([.,!?;–])', r' \1 ', sent)
        # Удаление нежелательных символов
        sent = re.sub(r'[^а-яА-ЯёЁA-Za-z0-9\s.,!?;\-–]', ' ', sent)
        # Замена многотокенных стоп-слов на уникальные маркеры
        for stopword in all_stopwords_sorted:
            stopword_tokens = stopword.split()
            if len(stopword_tokens) > 1:  # Если стоп-слово состоит из нескольких токенов
                pattern = r'\b' + r'\s+'.join(map(re.escape, stopword_tokens)) + r'\b'
                sent = re.sub(pattern, stopword.replace(' ', '_'), sent)
        # Разделение предложения на токены
        tokens = sent.strip().split()

        for i in range(len(tokens) - 2):
            trigram = tokens[i:i + 3]
            all_trigram_counts[tuple(trigram)] += 1

            stopword_count = sum(1 for token in trigram if token.replace('_', ' ') in all_stopwords)

            clean_trigram = [token.replace('_', ' ') for token in trigram]

            if stopword_count > 0:
                trigram_pos_with_at_least_one_func_w = [
                    token.replace('_', ' ') if token.replace('_', ' ') in all_stopwords
                    else get_pos(token.replace('_', ' '))
                    for token in trigram
                ]

                if stopword_count == 1:
                    func_words_contexts_with_tokens_or_pos['one_function_word'].append(
                        (clean_trigram, trigram_pos_with_at_least_one_func_w))
                    pos_trigram_counts['one_function_word'][tuple(trigram_pos_with_at_least_one_func_w)] += 1
                elif stopword_count == 2:
                    func_words_contexts_with_tokens_or_pos['two_function_words'].append(
                        (clean_trigram, trigram_pos_with_at_least_one_func_w))
                    pos_trigram_counts['two_function_words'][tuple(trigram_pos_with_at_least_one_func_w)] += 1
                elif stopword_count == 3:
                    func_words_contexts_with_tokens_or_pos['three_function_words'].append(
                        (clean_trigram, trigram_pos_with_at_least_one_func_w))
                    pos_trigram_counts['three_function_words'][tuple(trigram_pos_with_at_least_one_func_w)] += 1

            token_trigram_counts[tuple(clean_trigram)] += 1

    total_all_trigrams = sum(all_trigram_counts.values())

    normalized_freqs = {
        'one_function_word': {
            trigram: round(count / total_all_trigrams * 100, 3)
            for trigram, count in pos_trigram_counts['one_function_word'].items()
        },
        'two_function_words': {
            trigram: round(count / total_all_trigrams * 100, 3)
            for trigram, count in pos_trigram_counts['two_function_words'].items()
        },
        'three_function_words': {
            trigram: round(count / total_all_trigrams * 100, 3)
            for trigram, count in pos_trigram_counts['three_function_words'].items()
        }
    }

    sorted_normalized_freqs = {
        k: dict(sorted(v.items(), key=lambda item: item[1], reverse=True))
        for k, v in normalized_freqs.items()
    }

    pos_trigram_counts = {
        'one_function_word': dict(
            sorted(pos_trigram_counts['one_function_word'].items(), key=lambda item: item[1], reverse=True)),
        'two_function_words': dict(
            sorted(pos_trigram_counts['two_function_words'].items(), key=lambda item: item[1], reverse=True)),
        'three_function_words': dict(
            sorted(pos_trigram_counts['three_function_words'].items(), key=lambda item: item[1], reverse=True))
    }

    func_words_contexts_with_tokens_or_pos = dict(func_words_contexts_with_tokens_or_pos)

    def convert_keys_to_str(d):
        """
        Рекурсивно преобразует ключи словаря в строки.

        :param d: (dict или list): Словарь или список для преобразования.

        :return dict или list: Преобразованный словарь или список.
        """
        if isinstance(d, dict):
            return {str(k): convert_keys_to_str(v) for k, v in d.items()}
        elif isinstance(d, list):
            return [convert_keys_to_str(i) for i in d]
        else:
            return d

    sorted_normalized_freqs = convert_keys_to_str(sorted_normalized_freqs)
    pos_trigram_counts = convert_keys_to_str(pos_trigram_counts)
    func_words_contexts_with_tokens_or_pos = convert_keys_to_str(func_words_contexts_with_tokens_or_pos)
    sorted_normalized_freqs_json = json.dumps(sorted_normalized_freqs, ensure_ascii=False)
    pos_trigram_counts_json = json.dumps(pos_trigram_counts, ensure_ascii=False)
    func_words_contexts_with_tokens_or_pos_json = json.dumps(func_words_contexts_with_tokens_or_pos, ensure_ascii=False)

    if show_analysis:
        print_trigram_tables_with_func_w(sorted_normalized_freqs_json, pos_trigram_counts_json,
                                         func_words_contexts_with_tokens_or_pos_json)
    return sorted_normalized_freqs_json, pos_trigram_counts_json, func_words_contexts_with_tokens_or_pos_json


def print_trigram_tables_with_func_w(sorted_normalized_freqs, pos_trigram_counts_json, func_words_contexts_with_tokens_or_pos_json, for_corpus=False):
    """
    Выводит таблицы с данными о триграммах, содержащих функциональные слова, на основе предоставленных JSON-строк.

    :param sorted_normalized_freqs: JSON-строка, содержащая нормализованные частоты триграммов с функциональными словами.
    :param pos_trigram_counts_json: JSON-строка, содержащая абсолютные частоты триграммов с функциональными словами.
    :param func_words_contexts_with_tokens_or_pos_json: JSON-строка, содержащая контексты триграмм с функциональными словами.
    :param for_corpus: Булевый параметр. Если True, контексты не будут выводиться. По умолчанию False.

    Выводит таблицы с нормализованными частотами и абсолютными частотами триграммов в зависимости от минимальной частоты, указанной пользователем.
    Также запрашивает у пользователя, нужно ли вывести полные контексты триграммов с функциональными словами.
        """
    if for_corpus:
        print(
            Fore.LIGHTYELLOW_EX + Style.BRIGHT + "\n           ЧАСТОТЫ ЧАСТЕРЕЧНЫХ ТРИГРАММОВ С 1,2,3  ФУНКЦИОНАЛЬНЫМИ СЛОВАМИ" + Fore.RESET)
        wait_for_enter_to_analyze()
    sorted_normalized_freqs = json.loads(sorted_normalized_freqs)
    pos_trigram_counts = json.loads(pos_trigram_counts_json)
    func_words_contexts_with_tokens_or_pos = json.loads(func_words_contexts_with_tokens_or_pos_json)

    print(
        Fore.LIGHTGREEN_EX + Style.BRIGHT + "Введите интересующую Вас минимальную частоту триграммов или просто нажмите 'Enter' \n(по умолчанию значение=1):" + Fore.RESET)
    while True:
        min_frequency_input = input()
        if not min_frequency_input:
            min_frequency = 1
            break
        try:
            min_frequency = int(min_frequency_input)
            if min_frequency > 0:
                break
            else:
                print(Fore.LIGHTRED_EX + "Ошибка: Значение должно быть больше 0." + Fore.RESET)
        except ValueError:
            print(Fore.LIGHTRED_EX + "Ошибка: Введите числовое значение или нажмите 'Enter'.\n" + Fore.RESET)

    for category in ['one_function_word', 'two_function_words', 'three_function_words']:
        if category == 'one_function_word':
            show_text = 'ТРИГРАММЫ С ОДНИМ ФУНКЦИОНАЛЬНЫМ СЛОВОМ И ДВУМЯ МАРКЕРАМИ POS В СОСТАВЕ'
        elif category == 'two_function_words':
            show_text = 'ТРИГРАММЫ С ДВУМЯ ФУНКЦИОНАЛЬНЫМИ СЛОВАМИ И ОДНИМ МАРКЕРОМ POS В СОСТАВЕ'
        elif category == 'three_function_words':
            show_text = 'ТРИГРАММЫ С ТРЕМЯ ФУНКЦИОНАЛЬНЫМИ СЛОВАМИ В СОСТАВЕ'
        print(Fore.LIGHTYELLOW_EX + Style.BRIGHT + "\n* " + show_text + Fore.RESET)
        wait_for_enter_to_analyze()
        table = Table()
        table.add_column("Триграмм\n", no_wrap=True, style="bold", max_width=40)
        table.add_column("Абсолютная частота\n", justify="center", min_width=15)
        table.add_column("Нормализованная частота\n(%)", justify="center", min_width=15)

        # Объединяем данные из двух словарей
        normalized_freqs = sorted_normalized_freqs.get(category, {})
        pos_counts = pos_trigram_counts.get(category, {})
        sorted_data = dict(sorted(pos_counts.items(), key=lambda item: item[1], reverse=True))

        for trigram, count in sorted_data.items():
            if count >= min_frequency:
                freq = normalized_freqs.get(trigram, 0)
                table.add_row(str(trigram), str(count), f"{freq:.3f}%")

        console.print(table)
        wait_for_enter_to_analyze()

    if not for_corpus:
        print(
            Fore.LIGHTGREEN_EX + Style.BRIGHT + "\nВывести полные контексты триграммов с функциональными словами (y/n)? " + Fore.RESET)
        print(Fore.LIGHTRED_EX + Style.BRIGHT + "Внимание! Контексты могут занять много места на экране.")
        while True:
            choice = input().strip().lower()

            if choice == 'y':
                break
            elif choice == 'n':
                print(Fore.LIGHTRED_EX + Style.BRIGHT + "Вывод контекстов пропущен." + Fore.RESET)
                return
            else:
                print(Fore.LIGHTRED_EX + "\nНеверный ввод. Пожалуйста, введите 'y' или 'n'." + Fore.RESET)

        print(
            Fore.LIGHTYELLOW_EX + Style.BRIGHT + "\n            КОНТЕКСТЫ ЧАСТЕРЕЧНЫХ ТРИГРАММОВ С ФУНКЦИОНАЛЬНЫМИ СЛОВАМИ" + Fore.RESET)
        wait_for_enter_to_analyze()
        for category in ['one_function_word', 'two_function_words', 'three_function_words']:
            if category == 'one_function_word':
                show_text = 'ТРИГРАММОВ С ОДНИМ ФУНКЦИОНАЛЬНЫМ СЛОВОМ И ДВУМЯ МАРКЕРАМИ POS В СОСТАВЕ'
            elif category == 'two_function_words':
                show_text = 'ТРИГРАММОВ С ДВУМЯ ФУНКЦИОНАЛЬНЫМИ СЛОВАМИ И ОДНИМ МАРКЕРОМ POS В СОСТАВЕ'
            elif category == 'three_function_words':
                show_text = 'ТРИГРАММОВ С ТРЕМЯ ФУНКЦИОНАЛЬНЫМИ СЛОВАМИ В СОСТАВЕ'
            print(Fore.LIGHTYELLOW_EX + Style.BRIGHT + "\n* КОНТЕКСТЫ " + show_text + Fore.RESET)
            wait_for_enter_to_analyze()
            table = Table()
            table.add_column("С POS-тегами", no_wrap=True, width=40)
            table.add_column("Полные контексты в токенах", no_wrap=True, width=40)

            contexts = func_words_contexts_with_tokens_or_pos.get(category, [])
            for tokens, pos_tags in contexts:
                table.add_row(str(pos_tags), str(tokens))

            console.print(table)
            wait_for_enter_to_analyze()


if __name__ == "__main__":
    # Текст для примера (сгенерирован ИИ)
    text = """В огромном городе, где небоскрёбы касались облаков, жила девушка по имени Лиза. Она работала в 
       необычной организации под названием "Луч Света". Эта организация ставила перед собой амбициозную цель — помочь 
       каждому человеку на Земле и сделать мир добрее. Каждое утро Лиза приходила в светлый офис, наполненный зелёными 
       растениями и солнечными лучами, проникающими через огромные окна. Она садилась за свой стол и начинала день с 
       того, что проверяла письма и сообщения от людей со всего мира. Кто-то нуждался в помощи с оплатой медицинских 
       счетов, кто-то искал поддержку в трудную минуту, а кто-то просто хотел поделиться своей радостью. Однажды Лиза 
       получила письмо от маленькой девочки из далёкой деревни. Девочка писала, что её мама тяжело больна, 
       и она не знает, как ей помочь. Лиза немедленно связалась с коллегами, и вскоре команда врачей отправилась в ту 
       самую деревню, чтобы оказать необходимую помощь. Через несколько недель пришло радостное сообщение: мама девочки 
       пошла на поправку. Но "Луч Света" занимался не только экстренной помощью. Они организовывали образовательные 
       программы для детей из бедных семей, строили парки и школы, проводили акции по защите окружающей среды. Лиза 
       особенно гордилась проектом, который они запустили в Африке: благодаря усилиям команды, в нескольких деревнях 
       появились чистая вода и солнечные батареи. Однажды к ним в офис пришёл пожилой человек. Он выглядел растерянным и 
       усталым. Лиза подошла к нему и узнала, что его зовут Иван. Иван потерял всё: дом, семью, работу. Он чувствовал 
       себя одиноким и беспомощным. Лиза пригласила его в свой кабинет, выслушала его историю и пообещала помочь. В 
       течение нескольких дней команда "Луча Света" нашла для Ивана временное жильё, помогла восстановить документы и 
       устроить его на работу. Иван был бесконечно благодарен и часто заходил в офис, чтобы поделиться своими успехами. 
       Каждый вечер Лиза возвращалась домой с чувством выполненного долга. Она знала, что её работа имеет значение, 
       что люди, которым она помогла, снова верят в добро и справедливость. И хотя задачи, стоящие перед "Лучом Света", 
       казались порой непосильными, Лиза и её коллеги не сдавались. Они верили, что капля добра способна вызвать 
       настоящий океан перемен. Так проходили дни, месяцы и годы. Лиза продолжала работать в "Луче Света", 
       оставаясь верной своей мечте — сделать мир лучше. Она знала, что впереди ещё много вызовов, но с каждым добрым 
       делом, с каждой спасённой жизнью, с каждой улыбкой на лице благодарного человека мир становился чуть светлее и 
       добрее."""
    sorted_normalized_freqs, pos_trigram_counts, func_words_contexts_with_tokens_or_pos = contextual_function_words_in_trigrams(
        text)

