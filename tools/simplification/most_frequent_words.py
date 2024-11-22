# -*- coding: utf-8 -*- # Языковая кодировка UTF-8
import json
from collections import Counter, defaultdict

from colorama import Fore, Style
from rich.console import Console
from rich.table import Table

from tools.core.lemmatizators import lemmatize_words_without_stopwords
from tools.core.utils import wait_for_enter_to_analyze

console = Console()
patterns = r"[^А-Яа-яёЁa-zA-Z\-]+"


def count_types_in_text(text):
    """
    Лемматизирует текст, подсчитывает количество знаменательных частей речи и возвращает результат в формате JSON.

    Функция принимает текст, лемматизирует его, затем подсчитывает, как часто встречаются знаменательные части речи
    (существительные, глаголы, прилагательные и наречия). В конце результат выводится в формате JSON.

    :param text: Строка текста, который необходимо проанализировать.
    :return: JSON-объект, содержащий абсолютную частоту встречаемости знаменательных слов.
    """
    words = lemmatize_words_without_stopwords(text.lower(), patterns)
    word_list = [token.normal_form for token in words]
    significant_words_count = defaultdict(int)

    for word in word_list:
        significant_words_count[word] += 1

    result_json = json.dumps(significant_words_count, ensure_ascii=False, indent=4)

    return result_json


def find_n_most_frequent_words(text, values=(50,), show_analysis=True):
    """
    Выводит наиболее частотные слова в тексте с нормализованными частотами.

    :param text: Текст для анализа.
    :param values: Кортеж, содержащий количество наиболее частотных слов, которые нужно вывести. По умолчанию 50.
    :param show_analysis: Если True, выводит результаты в виде таблицы и ожидает нажатия клавиши для продолжения.
    :return: Строка, представляющая собой словарь наиболее частотных слов с нормализованными частотами.
    """
    words = lemmatize_words_without_stopwords(text.lower(), patterns)
    word_list = [token.normal_form for token in words]
    word_counts = Counter(word_list)
    total_words = sum(word_counts.values())
    normalized_frequencies = {word: round((count / total_words) * 100, 3) for word, count in word_counts.items()}

    frequent_words = {}
    for n in values:
        frequent_words[n] = dict(sorted(normalized_frequencies.items(), key=lambda item: item[1], reverse=True)[:n])

    if show_analysis:
        print(Fore.GREEN + Style.BRIGHT + "\n     НАИБОЛЕЕ ЧАСТОТНЫЕ 50 СЛОВ ТЕКСТА" + Fore.RESET)
        wait_for_enter_to_analyze()
        for n, words in frequent_words.items():
            table = Table()
            table.add_column("№", justify="center")
            table.add_column("Слово\n", style="bold")
            table.add_column("Нормализованная\nчастота (%)", justify="center")

            for idx, (word, freq) in enumerate(words.items(), start=1):
                table.add_row(str(idx), word, f"{freq}%")

            console.print(table)
            wait_for_enter_to_analyze()

    return str(frequent_words)


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
    a = count_types_in_text(text)
    print(a)
