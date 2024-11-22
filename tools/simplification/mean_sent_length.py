# -*- coding: utf-8 -*- # Языковая кодировка UTF-8
import re

from colorama import Fore, Style
from nltk.tokenize import word_tokenize
from rich.console import Console
from rich.table import Table

from tools.core.custom_punkt_tokenizer import sent_tokenize_with_abbr
from tools.core.utils import wait_for_enter_to_analyze
from tools.core.text_preparation import TextPreProcessor

console = Console()


def tokenize_with_punctuation(text):
    """
    Разделяет текст на токены, учитывая небуквенные знаки как отдельные токены.

    :param text (str): Текст для токенизации.
    :return list: Список токенов, включая знаки препинания.
    """
    tokens = word_tokenize(text, language="russian")
    return tokens


def mean_sentence_length_in_tokens(text, show_analysis=True):
    """
    Вычисляет среднюю длину предложения в токенах (включая знаки препинания).

    :param text: Текст для анализа.
    :param show_analysis: Если True, выводит результат в виде таблицы.
    :return float: Средняя длина предложений в токенах.
    """
    text_processor = TextPreProcessor()
    text = text_processor.fix_spacing_for_mean_sent_len(text)
    sentence_lengths = []
    sentences = sent_tokenize_with_abbr(text)

    # Подсчитываем токены в каждом предложении
    for sentence in sentences:
        tokens = tokenize_with_punctuation(sentence)
        sentence_lengths.append(len(tokens))

    mean_sent_length = round((sum(sentence_lengths) / len(sentence_lengths)), 3) if sentence_lengths else 0
    if show_analysis:
        # Создаем таблицу для вывода
        print(Fore.GREEN + Style.BRIGHT + "\n   СРЕДНЯЯ ДЛИНА ПРЕДЛОЖЕНИЙ В ТОКЕНАХ" + Fore.RESET)
        print(Fore.LIGHTRED_EX + Style.BRIGHT + "Знаки препинания считаются как токены." + Fore.RESET)
        table = Table()
        table.add_column("Показатель", style="bold")
        table.add_column("Значение", justify="center", min_width=10)

        table.add_row("Длина в токенах", str(mean_sent_length))
        table.add_row("Всего токенов", str(sum(sentence_lengths)))
        table.add_row("Всего предложений", str(len(sentence_lengths)))
        console.print(table)

        wait_for_enter_to_analyze()
    return mean_sent_length


def mean_sentence_length_in_chars(text, show_analysis=True):
    """
    Вычисляет среднюю длину предложения в символах (без учета пробелов).

    :param text: Текст для анализа.
    :param show_analysis: Если True, выводит результат в виде таблицы.
    :return float:  Средняя длина предложений в символах.
    """
    sentence_lengths = []
    sentences = sent_tokenize_with_abbr(text)

    # Подсчитываем количество символов в каждом предложении
    for sentence in sentences:
        cleaned_sentence = re.sub(r'\s+', '', sentence)  # Удаляем пробелы
        length = len(cleaned_sentence)
        sentence_lengths.append(length)

    mean_sent_length = round((sum(sentence_lengths) / len(sentence_lengths)), 3) if sentence_lengths else 0
    if show_analysis:
        print(Fore.GREEN + Style.BRIGHT + "\nСРЕДНЯЯ ДЛИНА ПРЕДЛОЖЕНИЙ В СИМВОЛАХ" + Fore.RESET)
        table = Table()
        table.add_column("Показатель", style="bold")
        table.add_column("Значение", justify="center", min_width=10)

        table.add_row("Длина в символах", str(mean_sent_length))
        table.add_row("Всего символов", str(sum(sentence_lengths)))
        table.add_row("Всего предложений", str(len(sentence_lengths)))
        console.print(table)
        wait_for_enter_to_analyze()

    return mean_sent_length


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
    mean_sentence_length_in_tokens(text)
    mean_sentence_length_in_chars(text)
