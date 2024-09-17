# -*- coding: utf-8 -*- # Языковая кодировка UTF-8
import math

import nltk
from colorama import Fore, Style
from rich.console import Console
from rich.table import Table

from tools.core.lemmatizators import lemmatize_words
from tools.core.text_preparation import TextPreProcessor
from tools.core.utils import wait_for_enter_to_analyze

console = Console()


def lexical_variety(text, show_analysis=True):
    """
     Рассчитывает лексическую вариативность текста, включая следующие метрики:

    1. **TTR (Type-Token Ratio)**: Соотношение типов (уникальных слов) к токенам (общему количеству слов) в процентах.
    2. **Log-TTR**: Логарифмическое соотношение типов к токенам, основанное на логарифмах их количества, в процентах.
    3. **Modified TTR**: Модифицированное соотношение типов к токенам, которое учитывает уникальные типы, встречающиеся
    только один раз в тексте.

    :param text : str
        Текст, для которого будет рассчитана лексическая вариативность.
    :return tuple(float, float, float)
        Кортеж из трех значений:
        - TTR (округленное до 3 знаков после запятой)
        - Log-TTR (округленное до 3 знаков после запятой)
        - Modified TTR (округленное до 3 знаков после запятой)
    """

    # Предобработка текста: замена аббревиатур и исправление пробелов
    text_processor = TextPreProcessor()
    text = text_processor.process_text(text)

    lemmatized_words_info = lemmatize_words(text)
    lemmatized_words = [token.normal_form for token in lemmatized_words_info]
    tokens_number = len(lemmatized_words)

    if tokens_number == 0:
        if show_analysis:
            print("В тексте нет слов для анализа лексического разнообразия.")
        return 0, 0, 0

    freq_dist = nltk.FreqDist(lemmatized_words)

    types = set(lemmatized_words)
    types_number = len(types)

    types_occur_once = sum(1 for count in freq_dist.values() if count == 1)

    # 1. TTR = V / N
    ttr = round((types_number / tokens_number) * 100, 3) if tokens_number > 0 else 0

    # 2. Log-TTR = log(V) / log(N)
    if tokens_number > 0 and types_number > 0:
        try:
            log_ttr = round((math.log(types_number) / math.log(tokens_number)) * 100, 3)
        except ZeroDivisionError:
            log_ttr = 0
    else:
        log_ttr = 0

    # 3. Modified TTR = 100 × log(N) / (1 - V1 / V)
    if types_number > 0:
        denominator = 1 - (types_occur_once / types_number)
        if denominator > 0:
            try:
                modified_ttr = round((100 * math.log(tokens_number)) / denominator, 3)
            except ZeroDivisionError:
                modified_ttr = 0
        else:
            modified_ttr = 0
    else:
        modified_ttr = 0

    if show_analysis:
        print(Fore.LIGHTYELLOW_EX + Style.BRIGHT + "\n       ЛЕКСИЧЕСКАЯ ВАРИАТИВНОСТЬ ТЕКСТА" + Fore.RESET)
        table = Table()

        table.add_column("Показатель", justify="left", no_wrap=True, min_width=30, style="bold")
        table.add_column("Значение", justify="center",  min_width=10)

        table.add_row("Лексическая вариативность (TTR)", f"{ttr}%")
        table.add_row("Логарифмический TTR", f"{log_ttr}%")
        table.add_row("Лексич. вариативность на основе\nуникальных типов", f"{modified_ttr}")
        table.add_row("\nКоличество типов", '\n' + str(types_number))
        table.add_row("Количество токенов", str(tokens_number))

        console.print(table)
        wait_for_enter_to_analyze()

        print(Fore.YELLOW + Style.BRIGHT + "\n                        ЧАСТОТНОЕ РАСПРЕДЕЛЕНИЕ ТИПОВ" + Fore.RESET)
        wait_for_enter_to_analyze()
        frequency_dict = {}
        for word, freq in freq_dist.items():
            if freq not in frequency_dict:
                frequency_dict[freq] = []
            frequency_dict[freq].append(word)

        table = Table()
        table.add_column("Частота", justify="center", width=10)
        table.add_column("Тип",  max_width=80)

        for freq in sorted(frequency_dict.keys(), reverse=True):
            words = ', '.join(frequency_dict[freq])
            table.add_row(str(freq), words)
        console.print(table)
        wait_for_enter_to_analyze()

    return ttr, log_ttr, modified_ttr


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
    ttr, log_ttr, modified_ttr = lexical_variety(text)
