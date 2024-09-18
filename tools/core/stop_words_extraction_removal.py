# -*- coding: utf-8 -*- # Языковая кодировка UTF-8
import re

from nltk.corpus import stopwords

from tools.core.data import pronouns, prepositions, particles, conjunctions
from tools.core.data.discource_markers import final_sci_dm_list

nltk_stopwords_ru = stopwords.words("russian")

# 1. Объединение всех списков stopwords в один
all_stopwords = set(conjunctions.conjunctions_list + prepositions.prepositions_list
                    + particles.particles_list + pronouns.pronouns_list + nltk_stopwords_ru)
# 2. Сортировка stopwords по длине по убыванию
all_stopwords_sorted = sorted(list(all_stopwords), key=len, reverse=True)


def count_custom_stopwords(text):
    """
    Подсчитывает количество стоп-слов в тексте.
    Args:
        text (str): Текст для анализа.
    Returns:
        tuple: Общее количество найденных стоп-слов, словарь, где ключи - это стоп-слова,
               а значения - количество их вхождений в текст, и общее количество вхождений всех стоп-слов в тексте.
    """
    stopword_counts = {stopword: 0 for stopword in all_stopwords_sorted}
    text_to_clean = text.lower()

    for stopword in all_stopwords_sorted:
        count = len(re.findall(r'\b' + re.escape(stopword) + r'\b', text_to_clean))
        if count > 0:
            stopword_counts[stopword] += count
            text_to_clean = re.sub(r'\b' + re.escape(stopword) + r'\b', '', text_to_clean)

    # Фильтруем только те стоп-слова, которые были найдены в тексте
    found_stopwords = {word: count for word, count in stopword_counts.items() if count > 0}
    sorted_stopwords = dict(sorted(found_stopwords.items(), key=lambda item: item[1], reverse=True))
    stopwords_total_count_with_rep = sum(found_stopwords.values())
    unique_stopwords = len(found_stopwords)

    # print(text_to_clean)
    # print(f"\nОбщее количество найденных стоп-слов (с учетом их повторений): {stopwords_total_count_with_rep}")
    # print(f"\nОбщее количество различных стоп-слов в тексте: {unique_stopwords}")
    # print("\nКоличество вхождений каждого найденного стоп-слова:\n")
    #
    # for stopword, count in sorted_stopwords.items():
    #     print(f"'{stopword}': {count} раз(а)")

    return stopwords_total_count_with_rep, sorted_stopwords, unique_stopwords


patterns = r"[^А-Яа-яёЁ\-]+"  # Оставляем только кириллицу и дефис


def remove_dm(text):
    """
    Функция удаляет дискурсивные маркеры из текста и считает их количество.

    Параметры:
    text (str): Входной текст, из которого удаляются маркеры.

    Возвращает:
    tuple: (обновленный текст без маркеров, количество удаленных маркеров)
    """
    # Преобразуем текст в нижний регистр для удобства поиска маркеров
    text_lower = text.lower()
    deleted_dms = 0

    # Проходим по каждому дискурсивному маркеру
    for dm in final_sci_dm_list:
        # Проверяем наличие маркера в тексте
        count_before = len(re.findall(r'\b' + re.escape(dm) + r'\b', text_lower))
        if count_before > 0:
            # Заменяем маркер на пустую строку
            text_lower = re.sub(r'\b' + re.escape(dm) + r'\b', '', text_lower)
            deleted_dms += count_before

    # Убираем лишние пробелы после удаления маркеров
    text_lower = re.sub(r'\s+', ' ', text_lower).strip()
    # Удаляем небуквенные символы
    text_cleaned = re.sub(r'[^а-яА-Яa-zA-Z\s]', '', text_lower)
    return text_cleaned, deleted_dms


if __name__ == "__main__":
    # Текст для примера (сгенерирован ИИ)
    text = """
    Таким образом, анализ проведенных исследований показал, что внедрение новых технологий значительно повысило эффективность работы компании. Однако, несмотря на положительные результаты, остались некоторые области, требующие дальнейшего улучшения. Подводя итог, можно сказать, что проект был успешным, но есть еще над чем работать. Подводя итоги, мы можем отметить, что команда справилась с поставленными задачами на высоком уровне    """

    a = remove_dm(text)
    print(a)
