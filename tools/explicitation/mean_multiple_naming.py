# -*- coding: utf-8 -*- # Языковая кодировка UTF-8
import ast

from colorama import Style, Fore
from rich.console import Console
from rich.table import Table

from tools.core.utils import wait_for_enter_to_analyze
from tools.explicitation.named_entities_extraction import extract_entities

console = Console()


def calculate_mean_multiple_naming(text, show_analysis=True):
    """
    Вычисляет среднее количество слов в именах собственных в тексте.

    :param text: Входной текст на русском языке для анализа имен собственных.
    :param show_analysis: Если True, отображает результаты анализа в виде таблицы (по умолчанию True).

    :return: Возвращает кортеж, включающий:
        - Среднее количество слов в именах собственных.
        - Строку с перечислением однословных имен.
        - Количество однословных имен.
        - Строку с перечислением многословных имен.
        - Количество многословных имен.
    """
    found_entities_str, entities_count = extract_entities(text, False)
    found_entities = ast.literal_eval(found_entities_str)  # Преобразуем строку в список кортежей

    single_entities = []
    multiple_entities = []

    lengths = []
    current_length = 0
    for entity, entity_type in found_entities:
        words = entity.split()
        # Распределяем сущности по спискам в зависимости от количества слов
        if len(words) == 1:
            single_entities.append(entity)
        else:
            multiple_entities.append(entity)

        if current_length == 0:
            current_length = len(entity.split())
        else:
            current_length += len(entity.split())
            lengths.append(current_length)
            current_length = 0
    if current_length > 0:
        lengths.append(current_length)

    single_entities_count = len(single_entities)
    multiple_entities_count = len(multiple_entities)
    mean_multiple_naming = round(sum(lengths) / entities_count, 3) if lengths else 0
    if show_analysis:
        print(Fore.LIGHTYELLOW_EX + Style.BRIGHT + "\n                СРЕДНЯЯ ДЛИНА ИМЕНОВАННЫХ СУЩНОСТЕЙ" + Fore.RESET)
        wait_for_enter_to_analyze()
        table = Table()

        table.add_column("Показатель", justify="left", no_wrap=True, min_width=30, style="bold")
        table.add_column("Значение", justify="left", max_width=80)

        table.add_row("Средняя длина в словах", f"{mean_multiple_naming}")
        table.add_row("Количество сущностей из 1 токена", str(single_entities_count))
        table.add_row("Количество сущностей из более\nчем 1 токена", str(multiple_entities_count))
        table.add_row("\nСущности из 1 токена", '\n' + ', '.join(single_entities))
        table.add_row("Сущности из более чем 1 токена", ', '.join(multiple_entities))

        console.print(table)
        wait_for_enter_to_analyze()

    return mean_multiple_naming, str(single_entities), single_entities_count, str(
        multiple_entities), multiple_entities_count


if __name__ == "__main__":
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
    calculate_mean_multiple_naming(text)
