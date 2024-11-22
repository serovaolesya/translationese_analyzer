# -*- coding: utf-8 -*-  # Языковая кодировка UTF-8
import json
import re
from collections import Counter, defaultdict

from colorama import init, Fore, Style
from nltk import word_tokenize
from rich.console import Console
from rich.table import Table

from tools.core.custom_punkt_tokenizer import sent_tokenize_with_abbr
from tools.core.utils import wait_for_enter_to_analyze, display_position_explanation
from tools.core.text_preparation import TextPreProcessor

init(autoreset=True)
console = Console()


def calculate_position_frequencies(text, show_analysis=True):
    """
    Вычисляет нормализованные частоты появления токенов на определенных позициях в предложениях.
    Позиции включают:
    - first: первый токен
    - second: второй токен
    - antepenultimate: предпредпоследний токен
    - penultimate: предпоследний токен
    - last: последний токен

    :param text (str): Входной текст для анализа
    :param show_analysis (bool): Флаг для отображения анализа (по умолчанию True).

    :return: JSON-объекты с нормализованными частотами токенов в позициях ('first', 'second', 'antepenultimate', 'penultimate', 'last')
        и абсолютными частотами токенов в этих позициях. Частоты округлены до 3 знаков после запятой.
    """
    if show_analysis:
        print(Fore.GREEN + Style.BRIGHT + "\n             ПОЗИЦИОННАЯ ЧАСТОТА ТОКЕНОВ\n" + Fore.RESET)
        print(
            Fore.LIGHTGREEN_EX + Style.BRIGHT + "Учитываются предложения, длина которых больше 5 токенов." + Fore.RESET)

    text_processor = TextPreProcessor()
    sentences = sent_tokenize_with_abbr(text)

    position_counts = defaultdict(Counter)
    total_sentences = 0

    for sent in sentences:
        sent = text_processor.process_text(sent)
        # Разделение слов и знаков препинания пробелами
        sent = re.sub(r'(["„”«»‘’.,!?;")(/\\])', r' \1 ', sent)
        sent = re.sub(r'[^а-яА-ЯёЁA-Za-z0-9\s.",)(!?;-]', '', sent)
        tokens = word_tokenize(sent, language="russian")
        if len(tokens) < 5:
            continue

        total_sentences += 1
        positions = {
            'first': tokens[0],
            'second': tokens[1],
            'antepenultimate': tokens[-3],
            'penultimate': tokens[-2],
            'last': tokens[-1]
        }

        for position, token in positions.items():
            position_counts[position][token] += 1

    normalized_frequencies = {}
    for position, counter in position_counts.items():
        normalized_frequencies[position] = dict(
            sorted(
                {token: round(count / total_sentences * 100, 3) for token, count in counter.items()}.items(),
                key=lambda item: item[1],
                reverse=True
            )
        )

    sorted_raw_counts = {}
    for position, counter in position_counts.items():
        sorted_raw_counts[position] = dict(
            sorted(counter.items(), key=lambda item: item[1], reverse=True)
        )

    frequencies = json.dumps(normalized_frequencies, ensure_ascii=False)
    raw_counts = json.dumps(sorted_raw_counts, ensure_ascii=False)

    if show_analysis:
        print_frequencies(frequencies, raw_counts)

    return frequencies, raw_counts


def min_count_choice_for_posiitions():
    """
    Запрашивает у пользователя минимальное значение для средней частоты токенов на позициях
    или использует значение по умолчанию (1), если пользователь ничего не вводит.

    Возвращает:
    float: Минимальное значение для средней частоты токенов.
    """
    while True:
        try:
            min_count_input = input(Fore.LIGHTGREEN_EX + Style.BRIGHT +
                                    f"\nВведите минимальное значение для средней частоты выводимых токенов на той или иной"
                                    f"\nпозиции или просто нажмите 'Enter', чтобы продолжить (по умолчанию значение=1): \n").strip()

            if not min_count_input:
                min_count = 1
                break
            else:
                min_count = float(min_count_input)
                if min_count <= 0:
                    print(Fore.LIGHTRED_EX + Style.BRIGHT + "\nОшибка! Значение не может быть < или = 0." + Fore.RESET)
                    continue
                break
        except ValueError:
            print(Fore.LIGHTRED_EX + Style.BRIGHT + "\nОшибка! Введите числовое значение." + Fore.RESET)
    return min_count


def print_frequencies(frequencies, raw_counts, min_count=1):
    """
    Выводит таблицы с частотами токенов на разных позициях.

    :param frequencies: JSON-строка с нормализованными частотами токенов.
    :param raw_counts: JSON-строка с абсолютными частотами токенов.
    :param min_count: Минимальное значение количества токенов для отображения (по умолчанию 1).

    """
    display_position_explanation()
    frequencies = json.loads(frequencies)
    raw_counts = json.loads(raw_counts)

    min_count = min_count_choice_for_posiitions()

    for position in ['first', 'second', 'antepenultimate', 'penultimate', 'last']:
        print(Fore.GREEN + Style.BRIGHT + f"             Токены на позиции: {position.capitalize()}")
        wait_for_enter_to_analyze()
        table = Table()
        table.add_column("Токен\n", no_wrap=True, min_width=15)
        table.add_column("Абсолютная частота", justify="center", width=15)
        table.add_column("Нормализованная частота (%)", justify="center", width=15)

        freq_data = frequencies.get(position, {})
        raw_data = raw_counts.get(position, {})

        sorted_tokens = sorted(freq_data.items(), key=lambda item: item[1], reverse=True)

        for token, freq in sorted_tokens:
            count = raw_data.get(token, 0)
            if count >= min_count:
                table.add_row(token, str(count), f"{freq:.2f}%")

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
    frequencies, counts = calculate_position_frequencies(text)
