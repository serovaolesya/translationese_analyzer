# -*- coding: utf-8 -*- # Языковая кодировка UTF-8
import ast
import json
import re
from collections import Counter

from colorama import Style, Fore
from rich.console import Console
from rich.table import Table

from data.discource_markers import (final_sci_dm_list, topic_intro_dm, info_sequence, illustration_dm,
                                    material_sequence, conclusion_dm, intro_new_addit_info,
                                    info_explanation_or_repetition,
                                    contrast_dm, examples_introduction_dm, author_opinion, categorical_attitude_dm,
                                    less_categorical_attitude_dm, call_to_action_dm, joint_action, putting_emphasis_dm,
                                    refer_to_background_knowledge)
from tools.core.utils import wait_for_enter_to_analyze
from tools.core.stop_words_extraction_removal import remove_dm

console = Console()


def sort_by_length(lst):
    """
    Сортирует список строк по убыванию длины строки.

    :param lst: Список строк для сортировки.
    :return: Отсортированный список строк.
    """
    return sorted(lst, key=len, reverse=True)


# Применение сортировки к каждому списку
topic_intro_dm = sort_by_length(topic_intro_dm)
info_sequence = sort_by_length(info_sequence)
illustration_dm = sort_by_length(illustration_dm)
material_sequence = sort_by_length(material_sequence)
conclusion_dm = sort_by_length(conclusion_dm)
intro_new_addit_info = sort_by_length(intro_new_addit_info)
info_explanation_or_repetition = sort_by_length(info_explanation_or_repetition)
contrast_dm = sort_by_length(contrast_dm)
examples_introduction_dm = sort_by_length(examples_introduction_dm)
author_opinion = sort_by_length(author_opinion)
categorical_attitude_dm = sort_by_length(categorical_attitude_dm)
less_categorical_attitude_dm = sort_by_length(less_categorical_attitude_dm)
call_to_action_dm = sort_by_length(call_to_action_dm)
joint_action = sort_by_length(joint_action)
putting_emphasis_dm = sort_by_length(putting_emphasis_dm)
refer_to_background_knowledge = sort_by_length(refer_to_background_knowledge)


def sci_dm_search(text, show_analysis=True):
    """
    Ищет дискурсивные маркеры (ДМ) научного текста в тексте и анализирует их.

    :param text: Текст для анализа.
    :param show_analysis: Флаг, указывающий, нужно ли выводить результаты анализа.

    :return: Кортеж с результатами анализа, включающий количество и частоту различных типов ДМ.
    """
    final_sci_dm_list.sort(key=len, reverse=True)
    pattern = re.compile(r'\b(?:' + '|'.join(map(re.escape, final_sci_dm_list)) + r')\b')
    lowercase_text = text.lower()
    only_alpha_text_without_stopwords, found_dm_num = remove_dm(lowercase_text)
    found_sci_dms = [m.group() for m in pattern.finditer(lowercase_text)]
    found_sci_dms_str = '; '.join(found_sci_dms)
    total_num_dms = len(found_sci_dms)
    marker_counts = Counter(found_sci_dms)

    marker_counts_str = json.dumps(dict(marker_counts), ensure_ascii=False)
    # print(marker_counts_str)
    total_tokens = len(only_alpha_text_without_stopwords.split()) + total_num_dms

    if total_tokens == 0:
        return (0, '', '', 0, '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, '', 0,
                0, '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, '', 0)

    # Analyze discourse marker types
    dm_type_counts = {
        "topic_intro_dm": [],
        "info_sequence": [],
        "illustration_dm": [],
        "material_sequence": [],
        "conclusion_dm": [],
        "intro_new_addit_info": [],
        "info_explanation_or_repetition": [],
        "contrast_dm": [],
        "examples_introduction_dm": [],
        "author_opinion": [],
        "categorical_attitude_dm": [],
        "less_categorical_attitude_dm": [],
        "call_to_action_dm": [],
        "joint_action": [],
        "putting_emphasis_dm": [],
        "refer_to_background_knowledge": [],
    }

    for dm in found_sci_dms:
        if dm in topic_intro_dm:
            dm_type_counts["topic_intro_dm"].append(dm)
        if dm in info_sequence:
            dm_type_counts["info_sequence"].append(dm)
        if dm in illustration_dm:
            dm_type_counts["illustration_dm"].append(dm)
        if dm in material_sequence:
            dm_type_counts["material_sequence"].append(dm)
        if dm in conclusion_dm:
            dm_type_counts["conclusion_dm"].append(dm)
        if dm in intro_new_addit_info:
            dm_type_counts["intro_new_addit_info"].append(dm)
        if dm in info_explanation_or_repetition:
            dm_type_counts["info_explanation_or_repetition"].append(dm)
        if dm in contrast_dm:
            dm_type_counts["contrast_dm"].append(dm)
        if dm in examples_introduction_dm:
            dm_type_counts["examples_introduction_dm"].append(dm)
        if dm in author_opinion:
            dm_type_counts["author_opinion"].append(dm)
        if dm in categorical_attitude_dm:
            dm_type_counts["categorical_attitude_dm"].append(dm)
        if dm in less_categorical_attitude_dm:
            dm_type_counts["less_categorical_attitude_dm"].append(dm)
        if dm in call_to_action_dm:
            dm_type_counts["call_to_action_dm"].append(dm)
        if dm in joint_action:
            dm_type_counts["joint_action"].append(dm)
        if dm in putting_emphasis_dm:
            dm_type_counts["putting_emphasis_dm"].append(dm)
        if dm in refer_to_background_knowledge:
            dm_type_counts["refer_to_background_knowledge"].append(dm)

    topic_intro_dm_str = "; ".join(dm_type_counts["topic_intro_dm"])
    topic_intro_dm_count = len(dm_type_counts["topic_intro_dm"])
    topic_intro_dm_freq = round(topic_intro_dm_count / total_tokens * 100, 3)

    info_sequence_str = "; ".join(dm_type_counts["info_sequence"])
    info_sequence_count = len(dm_type_counts["info_sequence"])
    info_sequence_freq = round(info_sequence_count / total_tokens * 100, 3)

    illustration_dm_str = "; ".join(dm_type_counts["illustration_dm"])
    illustration_dm_count = len(dm_type_counts["illustration_dm"])
    illustration_dm_freq = round(illustration_dm_count / total_tokens * 100, 3)

    material_sequence_str = "; ".join(dm_type_counts["material_sequence"])
    material_sequence_count = len(dm_type_counts["material_sequence"])
    material_sequence_freq = round(material_sequence_count / total_tokens * 100, 3)

    conclusion_dm_str = "; ".join(dm_type_counts["conclusion_dm"])
    conclusion_dm_count = len(dm_type_counts["conclusion_dm"])
    conclusion_dm_freq = round(conclusion_dm_count / total_tokens * 100, 3)

    intro_new_addit_info_str = "; ".join(dm_type_counts["intro_new_addit_info"])
    intro_new_addit_info_count = len(dm_type_counts["intro_new_addit_info"])
    intro_new_addit_info_freq = round(intro_new_addit_info_count / total_tokens * 100, 3)

    info_explanation_or_repetition_str = "; ".join(dm_type_counts["info_explanation_or_repetition"])
    info_explanation_or_repetition_count = len(dm_type_counts["info_explanation_or_repetition"])
    info_explanation_or_repetition_freq = round(info_explanation_or_repetition_count / total_tokens * 100, 3)

    contrast_dm_str = "; ".join(dm_type_counts["contrast_dm"])
    contrast_dm_count = len(dm_type_counts["contrast_dm"])
    contrast_dm_freq = round(contrast_dm_count / total_tokens * 100, 3)

    examples_introduction_dm_str = "; ".join(dm_type_counts["examples_introduction_dm"])
    examples_introduction_dm_count = len(dm_type_counts["examples_introduction_dm"])
    examples_introduction_dm_freq = round(examples_introduction_dm_count / total_tokens * 100, 3)

    author_opinion_str = "; ".join(dm_type_counts["author_opinion"])
    author_opinion_count = len(dm_type_counts["author_opinion"])
    author_opinion_freq = round(author_opinion_count / total_tokens * 100, 3)

    categorical_attitude_dm_str = "; ".join(dm_type_counts["categorical_attitude_dm"])
    categorical_attitude_dm_count = len(dm_type_counts["categorical_attitude_dm"])
    categorical_attitude_dm_freq = round(categorical_attitude_dm_count / total_tokens * 100, 3)

    less_categorical_attitude_dm_str = "; ".join(dm_type_counts["less_categorical_attitude_dm"])
    less_categorical_attitude_dm_count = len(dm_type_counts["less_categorical_attitude_dm"])
    less_categorical_attitude_dm_freq = round(less_categorical_attitude_dm_count / total_tokens * 100, 3)

    call_to_action_dm_str = "; ".join(dm_type_counts["call_to_action_dm"])
    call_to_action_dm_count = len(dm_type_counts["call_to_action_dm"])
    call_to_action_dm_freq = round(call_to_action_dm_count / total_tokens * 100, 3)

    joint_action_str = "; ".join(dm_type_counts["joint_action"])
    joint_action_count = len(dm_type_counts["joint_action"])
    joint_action_freq = round(joint_action_count / total_tokens * 100, 3)

    putting_emphasis_dm_str = "; ".join(dm_type_counts["putting_emphasis_dm"])
    putting_emphasis_dm_count = len(dm_type_counts["putting_emphasis_dm"])
    putting_emphasis_dm_freq = round(putting_emphasis_dm_count / total_tokens * 100, 3)

    refer_to_background_knowledge_str = "; ".join(dm_type_counts["refer_to_background_knowledge"])
    refer_to_background_knowledge_count = len(dm_type_counts["refer_to_background_knowledge"])
    refer_to_background_knowledge_freq = round(refer_to_background_knowledge_count / total_tokens * 100, 3)

    if show_analysis:
        print_dm_analysis_results(
            total_num_dms, marker_counts_str,
            topic_intro_dm_count, topic_intro_dm_str, topic_intro_dm_freq,
            info_sequence_count, info_sequence_str, info_sequence_freq,
            illustration_dm_count, illustration_dm_str, illustration_dm_freq,
            material_sequence_count, material_sequence_str, material_sequence_freq,
            conclusion_dm_count, conclusion_dm_str, conclusion_dm_freq,
            intro_new_addit_info_count, intro_new_addit_info_str, intro_new_addit_info_freq,
            info_explanation_or_repetition_count, info_explanation_or_repetition_str,
            info_explanation_or_repetition_freq,
            contrast_dm_count, contrast_dm_str, contrast_dm_freq,
            examples_introduction_dm_count, examples_introduction_dm_str, examples_introduction_dm_freq,
            author_opinion_count, author_opinion_str, author_opinion_freq,
            categorical_attitude_dm_count, categorical_attitude_dm_str, categorical_attitude_dm_freq,
            less_categorical_attitude_dm_count, less_categorical_attitude_dm_str, less_categorical_attitude_dm_freq,
            call_to_action_dm_count, call_to_action_dm_str, call_to_action_dm_freq,
            joint_action_count, joint_action_str, joint_action_freq,
            putting_emphasis_dm_count, putting_emphasis_dm_str, putting_emphasis_dm_freq,
            refer_to_background_knowledge_count, refer_to_background_knowledge_str, refer_to_background_knowledge_freq,
        )

    return (total_num_dms, found_sci_dms_str, marker_counts_str,
            topic_intro_dm_count, topic_intro_dm_str, topic_intro_dm_freq,
            info_sequence_count, info_sequence_str, info_sequence_freq,
            illustration_dm_count, illustration_dm_str, illustration_dm_freq,
            material_sequence_count, material_sequence_str, material_sequence_freq,
            conclusion_dm_count, conclusion_dm_str, conclusion_dm_freq,
            intro_new_addit_info_count, intro_new_addit_info_str, intro_new_addit_info_freq,
            info_explanation_or_repetition_count, info_explanation_or_repetition_str,
            info_explanation_or_repetition_freq,
            contrast_dm_count, contrast_dm_str, contrast_dm_freq,
            examples_introduction_dm_count, examples_introduction_dm_str, examples_introduction_dm_freq,
            author_opinion_count, author_opinion_str, author_opinion_freq,
            categorical_attitude_dm_count, categorical_attitude_dm_str, categorical_attitude_dm_freq,
            less_categorical_attitude_dm_count, less_categorical_attitude_dm_str, less_categorical_attitude_dm_freq,
            call_to_action_dm_count, call_to_action_dm_str, call_to_action_dm_freq,
            joint_action_count, joint_action_str, joint_action_freq,
            putting_emphasis_dm_count, putting_emphasis_dm_str, putting_emphasis_dm_freq,
            refer_to_background_knowledge_count, refer_to_background_knowledge_str, refer_to_background_knowledge_freq,
            )


def print_dm_analysis_results(total_num_dms, marker_counts_str,
                              topic_intro_dm_count, topic_intro_dm_str, topic_intro_dm_freq,
                              info_sequence_count, info_sequence_str, info_sequence_freq,
                              illustration_dm_count, illustration_dm_str, illustration_dm_freq,
                              material_sequence_count, material_sequence_str, material_sequence_freq,
                              conclusion_dm_count, conclusion_dm_str, conclusion_dm_freq,
                              intro_new_addit_info_count, intro_new_addit_info_str, intro_new_addit_info_freq,
                              info_explanation_or_repetition_count, info_explanation_or_repetition_str,
                              info_explanation_or_repetition_freq,
                              contrast_dm_count, contrast_dm_str, contrast_dm_freq,
                              examples_introduction_dm_count, examples_introduction_dm_str,
                              examples_introduction_dm_freq,
                              author_opinion_count, author_opinion_str, author_opinion_freq,
                              categorical_attitude_dm_count, categorical_attitude_dm_str, categorical_attitude_dm_freq,
                              less_categorical_attitude_dm_count, less_categorical_attitude_dm_str,
                              less_categorical_attitude_dm_freq,
                              call_to_action_dm_count, call_to_action_dm_str, call_to_action_dm_freq,
                              joint_action_count, joint_action_str, joint_action_freq,
                              putting_emphasis_dm_count, putting_emphasis_dm_str, putting_emphasis_dm_freq,
                              refer_to_background_knowledge_count, refer_to_background_knowledge_str,
                              refer_to_background_knowledge_freq):
    """
        Выводит результаты анализа дискурсивных маркеров (ДМ).

    :param total_num_dms: Общее количество найденных ДМ.
    :param marker_counts_str: Строка JSON с количеством найденных маркеров.
    :param some_dm_count: Количество ДМ.
    :param some_dm_str: Строка с ДМ.
    :param some_dm_freq: Нормализованная частота ДМ.
    """

    marker_counts = ast.literal_eval(marker_counts_str)

    print(
        Fore.LIGHTYELLOW_EX + Style.BRIGHT + "\n            НАЙДЕННЫЕ ДИСКУРСИВНЫЕ МАРКЕРЫ И КОЛИЧЕСТВА ИХ ВХОЖДЕНИЙ" + Fore.RESET)
    print(Fore.LIGHTGREEN_EX + Style.BRIGHT + f"* Всего найдено {total_num_dms} ДМ" + Fore.RESET)

    table1 = Table()
    table1.add_column("Категория ДМ", justify="left")
    table1.add_column("Маркеры", justify="left")

    def add_marker_rows(category_name, dm_str):
        markers = dm_str.split("; ")
        unique_markers = set(markers)
        markers_with_count = [f"{dm} ({marker_counts.get(dm, 0)})" for dm in unique_markers]
        table1.add_row(category_name, ', '.join(markers_with_count))

    if topic_intro_dm_count:
        add_marker_rows("Введение в тему", topic_intro_dm_str)
    if info_sequence_count:
        add_marker_rows("Порядок следования информации", info_sequence_str)
    if illustration_dm_count:
        add_marker_rows("Иллюстративный материал", illustration_dm_str)
    if material_sequence_count:
        add_marker_rows("Порядок расположения материала", material_sequence_str)
    if conclusion_dm_count:
        add_marker_rows("Вывод/заключение", conclusion_dm_str)
    if intro_new_addit_info_count:
        add_marker_rows("Введение новой/доп. информации", intro_new_addit_info_str)
    if info_explanation_or_repetition_count:
        add_marker_rows("Повтор/конкретизация информации", info_explanation_or_repetition_str)
    if contrast_dm_count:
        add_marker_rows("Противопоставление", contrast_dm_str)
    if examples_introduction_dm_count:
        add_marker_rows("Введение примеров", examples_introduction_dm_str)
    if author_opinion_count:
        add_marker_rows("Мнение автора", author_opinion_str)
    if categorical_attitude_dm_count:
        add_marker_rows("Категоричная оценка", categorical_attitude_dm_str)
    if less_categorical_attitude_dm_count:
        add_marker_rows("Менее категоричная оценка", less_categorical_attitude_dm_str)
    if call_to_action_dm_count:
        add_marker_rows("Призыв к действию", call_to_action_dm_str)
    if joint_action_count:
        add_marker_rows("Совместное действие", joint_action_str)
    if putting_emphasis_dm_count:
        add_marker_rows("Акцентирование внимания", putting_emphasis_dm_str)
    if refer_to_background_knowledge_count:
        add_marker_rows("Отсылка к фоновым знаниям", refer_to_background_knowledge_str)

    console.print(table1)
    wait_for_enter_to_analyze()

    print(
        Fore.LIGHTYELLOW_EX + Style.BRIGHT + "\n              ЧАСТОТЫ НАЙДЕННЫХ ДИСКУРСИВНЫХ МАРКЕРОВ ПО КАТЕГОРИЯМ" + Fore.RESET)
    table2 = Table()
    table2.add_column("Категория ДМ\n", justify="left")
    table2.add_column("Абсолютная частота\n", justify="center")
    table2.add_column("Нормализованная частота\n (%)", justify="center")

    # Собираем данные в список
    frequency_data = [
        ("Введение в тему", topic_intro_dm_count, topic_intro_dm_freq),
        ("Порядок следования информации", info_sequence_count, info_sequence_freq),
        ("Иллюстративный материал", illustration_dm_count, illustration_dm_freq),
        ("Порядок расположения материала", material_sequence_count, material_sequence_freq),
        ("Вывод/заключение", conclusion_dm_count, conclusion_dm_freq),
        ("Введение новой/доп. информации", intro_new_addit_info_count, intro_new_addit_info_freq),
        ("Повтор/конкретизация информации", info_explanation_or_repetition_count, info_explanation_or_repetition_freq),
        ("Противопоставление", contrast_dm_count, contrast_dm_freq),
        ("Введение примеров", examples_introduction_dm_count, examples_introduction_dm_freq),
        ("Мнение автора", author_opinion_count, author_opinion_freq),
        ("Категоричная оценка", categorical_attitude_dm_count, categorical_attitude_dm_freq),
        ("Менее категоричная оценка", less_categorical_attitude_dm_count, less_categorical_attitude_dm_freq),
        ("Призыв к действию", call_to_action_dm_count, call_to_action_dm_freq),
        ("Совместное действие", joint_action_count, joint_action_freq),
        ("Акцентирование внимания", putting_emphasis_dm_count, putting_emphasis_dm_freq),
        ("Отсылка к фоновым знаниям", refer_to_background_knowledge_count, refer_to_background_knowledge_freq),
    ]

    # Фильтрация по частоте > 0
    frequency_data = [(cat, count, freq) for cat, count, freq in frequency_data if count > 0]
    # Сортировка по абсолютной частоте в порядке убывания
    frequency_data_sorted = sorted(frequency_data, key=lambda x: x[1] or 0, reverse=True)

    for category_name, count, freq in frequency_data_sorted:
        if count is not None:
            table2.add_row(category_name, str(count), f"{freq:.3f}%")

    console.print(table2)
    wait_for_enter_to_analyze()


if __name__ == "__main__":
    # Текст для примера (сгенерирован ИИ)
    text = """Исследования показывают, что с увеличением температуры многие виды растений начинают цветение на 
    несколько недель раньше, чем это было зафиксировано в прошлом веке. Это явление особенно заметно в умеренных 
    широтах, где сезонные изменения температуры наиболее выражены. Например, анализ данных за последние 50 лет 
    показал, что средняя дата начала цветения для ряда видов флоры Северной Америки и Европы сместилась на 10–15 дней 
    раньше. Такие сдвиги могут нарушить синхронизацию между растениями и их опылителями, что потенциально угрожает 
    успешному размножению. Смещение ареалов обитания растений является одной из наиболее очевидных реакций на 
    изменение климата. По мере повышения температуры виды стремятся мигрировать в более прохладные регионы, 
    такие как горные районы или более высокие широты. Однако скорость изменений климата зачастую превышает 
    способности видов к миграции, что приводит к сокращению их популяций и даже к локальному или глобальному 
    вымиранию. Наше моделирование показало, что при сценарии повышения глобальной температуры на 2°C до конца XXI 
    века, порядка 20% изученных видов растений будут вынуждены сместиться на север или в более высокие горные районы. 
    В частности, виды, обитающие на низких широтах и в равнинных регионах, окажутся под наибольшим давлением. Виды, 
    обладающие узкой экологической нишей и ограниченными возможностями для миграции, как, например, эндемики горных 
    экосистем, наиболее уязвимы к этим изменениям."""
    sci_dm_search(text)
