# -*- coding: utf-8 -*- # Языковая кодировка UTF-8
import re

from colorama import Fore, Style
from rich.console import Console
from rich.table import Table

from tools.core.utils import wait_for_enter_to_analyze
from tools.core.lemmatizators import lemmatize_words
from tools.stop_words_extraction_removal import all_stopwords_sorted
from tools.core.text_preparation import TextPreProcessor

console = Console()

# Предкомпилируем регулярные выражения
compiled_patterns = re.compile(r"[^А-Яа-яёЁa-zA-Z0-9\-]+")
compiled_stopwords = [re.compile(r'\b' + re.escape(stopword) + r'\b', re.IGNORECASE) for stopword in
                      all_stopwords_sorted]

def remove_stopwords(text, stopwords):
    """Удаляем стоп-слова из текста и подсчитываем количество удаленных слов."""
    stopwords_count = 0
    for pattern in stopwords:
        matches = pattern.findall(text)
        stopwords_count += len(matches)
        text = pattern.sub('', text)
    return re.sub(r'\s+', ' ', text).strip(), stopwords_count


def calculate_lexical_density(text, show_analysis=True):
    """
    Рассчитывает лексическую плотность текста, определяя соотношение
    знаменательных слов (содержательных частей речи, а именно глаголов,
    существительных, прилагательных и наречий) к общему количеству
    слов в тексте.

    :param text (str): Входной текст для анализа.
    :param show_analysis: Boolean.
    :return float: лексическая плотность текста, выраженная в процентах.
    """

    # Предобработка текста: замена аббревиатур и исправление пробелов
    text_processor = TextPreProcessor()
    text = text_processor.process_text(text)

    # Используем предкомпилированное регулярное выражение
    text = compiled_patterns.sub(' ', text)
    all_words = len(re.findall(r'\b\w+\b', text))

    text_without_stopwords, stopwords_count = remove_stopwords(text, compiled_stopwords)
    words = lemmatize_words(text_without_stopwords)
    content_words = [token.normal_form for token in words if
                     token.tag.POS in {'NOUN', 'VERB', 'INFN', 'PRTF', 'PRTS', 'GRND', 'PRED', 'ADJF', 'ADJS', 'COMP',
                                       'ADVB'} and token.normal_form not in {'быть', 'являться'}]
    if len(content_words) == 0:
        if show_analysis:
            print(Fore.LIGHTYELLOW_EX + Style.BRIGHT + "\n        ЛЕКСИЧЕСКАЯ ПЛОТНОСТЬ ТЕКСТА")
            print(Fore.LIGHTWHITE_EX + "В тексте нет слов для анализа лексической плотности.")
        return 0
    lexical_density = round(len(content_words) / all_words * 100, 3)

    if show_analysis:
        print(Fore.LIGHTYELLOW_EX + Style.BRIGHT + "\n        ЛЕКСИЧЕСКАЯ ПЛОТНОСТЬ ТЕКСТА" + Fore.RESET)

        table = Table()
        table.add_column("Параметр", justify="left", no_wrap=True, min_width=30, style="bold")
        table.add_column("Значение", justify="center", min_width=10)

        table.add_row("Лексическая плотность", f"{lexical_density:.2f}%")
        table.add_row("\nОбщее количество слов в тексте", '\n' + str(all_words))
        table.add_row("Количество знаменательных слов", str(len(content_words)))

        console.print(table)
        wait_for_enter_to_analyze()

    return lexical_density


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
    calculate_lexical_density(text)
