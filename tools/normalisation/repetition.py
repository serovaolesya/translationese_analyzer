# -*- coding: utf-8 -*- # Языковая кодировка UTF-8
import json
from collections import defaultdict

from colorama import Fore, Style
from rich.console import Console
from rich.table import Table

from tools.core.utils import wait_for_enter_to_analyze
from tools.core.lemmatizators import lemmatize_words_without_stopwords
from tools.stop_words_extraction_removal import count_custom_stopwords
from tools.core.text_preparation import TextPreProcessor

console = Console()
patterns = r"[^А-Яа-яёЁa-zA-Z\-]+"


def calculate_repetition(text, show_analysis=True):
    """
    Рассчитывает повторяемость знаменательных слов в тексте и предоставляет информацию о количестве повторяющихся слов.

    :param text: str, Текст для анализа.
    :param show_analysis: bool, Если True, промежуточные результаты и таблицы будут отображены. По умолчанию True.
    :return: tuple (float, str, int, int)
        - repetition: float, Процент повторяемости содержательных слов в тексте.
        - sorted_content_word_counts_json: str, JSON-строка с количеством вхождений знаменательных слов.
        - repeated_content_words_num: int, Количество повторяющихся знаменательных слов.
        - total_word_tokens_count: int, Общее количество словарных токенов.
    """
    if show_analysis:
        print(Fore.LIGHTYELLOW_EX + Style.BRIGHT + "\n                             ПОВТОРЯЕМОСТЬ ЗНАМЕНАТЕЛЬНЫХ СЛОВ" + Fore.RESET)
        print(
            Fore.LIGHTRED_EX + Style.BRIGHT + "Внимание! В зависимости от размера текста подсчет повторяемости может занять какое-то время. \nПожалуйста, будьте готовы подождать.\n" + Fore.RESET)

        wait_for_enter_to_analyze()
    text_processor = TextPreProcessor()
    text = text_processor.fix_spacing(text)
    lemmatized_tokens = lemmatize_words_without_stopwords(text.lower(), patterns)
    content_word_counts = {}
    stopwords_count, found_stopwords_dict, unique_stopwords = count_custom_stopwords(text)

    # Подсчет лемм "являться"
    link_verb_lemmas = sum(1 for token in lemmatized_tokens if token.normal_form in 'являться')

    total_word_tokens_count = len(lemmatized_tokens) + stopwords_count + link_verb_lemmas

    for token in lemmatized_tokens:
        # Проверяем, является ли слово знаменательным (существительное, глагол, прилагательное, наречие)
        if token.tag.POS in {'NOUN', 'VERB', 'INFN', 'PRTF', 'PRTS', 'GRND', 'PRED', 'ADJF', 'ADJS', 'COMP',
                             'ADVB'} and token.normal_form not in {'быть', 'являться'}:
            content_word_counts[token.normal_form] = content_word_counts.get(token.normal_form, 0) + 1

    # Подсчитываем, сколько знаменательных слов встречаются больше одного раза
    repeated_content_words_num = sum(count - 1 for count in content_word_counts.values() if count > 1)
    sorted_content_word_counts = dict(sorted(content_word_counts.items(), key=lambda item: item[1], reverse=True))

    if total_word_tokens_count > 0:
        repetition = round(repeated_content_words_num / total_word_tokens_count * 100, 3)
        if show_analysis:
            table = Table()

            table.add_column("Показатель", style="bold")
            table.add_column("Значение",  justify="center")

            table.add_row("Повторяемость", str(repetition) + '%')
            table.add_row("Количество повторяющихся знаменательных слов", str(repeated_content_words_num))
            table.add_row("Общее количество словарных токенов", str(total_word_tokens_count))

            console.print(table)
            wait_for_enter_to_analyze()

        sorted_content_word_counts_json = json.dumps(sorted_content_word_counts, ensure_ascii=False, indent=4)
        if show_analysis:
            print_word_occurrences_table(sorted_content_word_counts_json)

        return repetition, sorted_content_word_counts_json, repeated_content_words_num, total_word_tokens_count

    else:
        if show_analysis:
            print("\n* Ввод пуст.")

        return 0, json.dumps({}, ensure_ascii=False, indent=4), 0, 0


def print_word_occurrences_table(sorted_content_word_counts_json, min_occurrences=2):
    """
    Выводит таблицу с количеством вхождений знаменательных слов, начиная с заданного минимального значения.

    :param sorted_content_word_counts_json: str, JSON-строка с количеством вхождений знаменательных слов.
    :param min_occurrences: int, Минимальное количество вхождений для отображения в таблице. Значение по умолчанию 2.
    """
    # Преобразование строки JSON обратно в словарь
    print(Fore.YELLOW + Style.BRIGHT + "\n                КОЛИЧЕСТВА ВХОЖДЕНИЙ ЗНАМЕНАТЕЛЬНЫХ СЛОВ" + Fore.RESET)
    while True:
        try:
            user_input = input(Fore.LIGHTGREEN_EX + Style.BRIGHT +
                               "Введите минимальное значение для отображения количества вхождений или нажмите "
                               "\n'Enter', чтобы пропустить выбор (по умолчанию значение=2):" + Fore.RESET).strip()
            if not user_input:
                break  # Значение по умолчанию, если пользователь ничего не ввел
            min_occurrences = int(user_input)
            if min_occurrences > 0:
                break
            else:
                print(Fore.RED + "Минимальное количество вхождений должно быть больше нуля.\n" + Fore.RESET)
        except ValueError:
            print(Fore.RED + "Пожалуйста, введите целое число." + Fore.RESET)

    try:
        sorted_content_word_counts = json.loads(sorted_content_word_counts_json)
    except json.JSONDecodeError as e:
        print(Fore.LIGHTRED_EX + Style.BRIGHT + f"Ошибка парсинга JSON: {e}" + Fore.RESET)
        return

    word_table = Table()

    word_table.add_column("Кол-во вхождений", style="bold", justify="center", min_width=15)
    word_table.add_column("Слова", max_width=80)

    grouped_word_counts = defaultdict(list)
    for word, count in sorted_content_word_counts.items():
        if count >= min_occurrences:
            grouped_word_counts[count].append(word)

    if not grouped_word_counts:
        print(Fore.RED + Style.BRIGHT + "\nНет слов с количеством вхождений > или = указанному минимуму." + Fore.RESET)
        return

    for count, words in sorted(grouped_word_counts.items(), reverse=True):
        word_table.add_row(str(count), ", ".join(words))

    console.print(word_table)


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
    repetitions, content_word_count, repeated_words, total_tokens = calculate_repetition(text)
