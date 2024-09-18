# -*- coding: utf-8 -*- # Языковая кодировка UTF-8
import json
from collections import Counter

from colorama import Fore, Style
from rich.console import Console
from rich.table import Table

from tools.core.data.pronouns import pronouns_analysis_list
from tools.core.utils import wait_for_enter_to_analyze
from tools.core.lemmatizators import lemmatize_words

console = Console()


def compute_pronoun_frequencies(text, show_analysis=True):
    """
    Вычисляет абсолютные и нормализованные частоты местоимений в тексте.

    :param text: Входной текст на русском языке.
    :param show_analysis: Определяет, выводить ли анализ в терминал.

    :return: JSON-строка с нормализованными частотами местоимений и JSON-строка сабсолютными частотами.
    """
    tokens_info = lemmatize_words(text)
    token_counts = Counter()
    pronoun_frequencies = {}

    # Подсчёт частот всех токенов
    for token in tokens_info:
        token_counts[token.normal_form] += 1

    # Подсчёт частот только местоимений
    pronoun_counts = {pronoun: token_counts[pronoun] for pronoun in pronouns_analysis_list if pronoun in token_counts}

    total_tokens_count = sum(token_counts.values())

    if total_tokens_count > 0:
        pronoun_frequencies = {k: (v / total_tokens_count) * 100 for k, v in pronoun_counts.items()}

    # Сортировка по частоте
    sorted_pronoun_frequencies = sorted(pronoun_frequencies.items(), key=lambda item: item[1], reverse=True)
    rounded_pronoun_frequencies = {pronoun: round(frequency, 3) for pronoun, frequency in sorted_pronoun_frequencies}

    sorted_pronoun_counts = sorted(pronoun_counts.items(), key=lambda item: item[1], reverse=True)

    pronoun_freqs_json = json.dumps(rounded_pronoun_frequencies, ensure_ascii=False)
    pronoun_counts_json = json.dumps(dict(sorted_pronoun_counts), ensure_ascii=False)
    if show_analysis:
        print_pronoun_frequencies(pronoun_freqs_json, pronoun_counts_json)
        wait_for_enter_to_analyze()

    return pronoun_freqs_json, pronoun_counts_json


def print_pronoun_frequencies(pronoun_freqs_json, pronoun_counts_json):
    """
    Печатает абсолютные и нормализованные частоты местоимений .

    :param pronoun_freqs_json: JSON-строка с нормализованными частотами местоимений.
    :param pronoun_counts_json: JSON-строка с абсолютными частотами местоимений.
    """
    frequencies = json.loads(pronoun_freqs_json)
    counts = json.loads(pronoun_counts_json)
    print(Fore.LIGHTYELLOW_EX + Style.BRIGHT + "\n                           ЧАСТОТЫ МЕСТОИМЕНИЙ" + Fore.RESET)

    table = Table()
    table.add_column("Местоимение\n", justify="center", style="bold", min_width=20)
    table.add_column("Абсолютная частота\n", justify="center", min_width=20)
    table.add_column("Нормализованная частота \n(%)", justify="center", min_width=20)

    for pronoun, frequency in frequencies.items():
        count = counts.get(pronoun, 0)  # Получаем количество для местоимения
        table.add_row(pronoun, str(count), f"{frequency:.3f}%")

    console.print(table)


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
    frequencies_json, a = compute_pronoun_frequencies(text)
