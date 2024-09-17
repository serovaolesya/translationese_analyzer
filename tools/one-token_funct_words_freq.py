# -*- coding: utf-8 -*- # Языковая кодировка UTF-8
import re

from collections import defaultdict

import pymorphy2
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

from data import conjunctions, discource_markers, particles, prepositions, pronouns

# Загрузка стоп-слов
nltk_stopwords_ru = stopwords.words("russian")

# 1. Объединение всех списков в один
all_stopwords = set(conjunctions.conjunctions_list + prepositions.prepositions_list
                    + particles.particles_list + pronouns.pronouns_list + nltk_stopwords_ru)

# 2. Сортировка по длине по убыванию
all_stopwords_sorted = sorted(list(all_stopwords), key=len, reverse=True)

morph = pymorphy2.MorphAnalyzer()


def compute_function_word_frequencies(text):
    text = re.sub(r'[^а-яА-ЯËёa-zA-Z\-]', ' ', text)

    function_word_counts = defaultdict(int)

    # Токенизация текста
    tokens = word_tokenize(text.lower())  # Приведение к нижнему регистру для сопоставления
    total_tokens = len(tokens)
    # print(total_tokens)

    # Подсчет частоты каждого функции слова
    for token in tokens:
        token = morph.parse(token)[0]
        lemmatized_token = token.normal_form
        if lemmatized_token in all_stopwords_sorted:
            function_word_counts[lemmatized_token] += 1

    # Нормализация частоты
    normalized_frequencies = {word: round((count / total_tokens) * 100, 3) for word, count in function_word_counts.items()}

    # Сортировка по убыванию частоты
    sorted_frequencies = dict(sorted(normalized_frequencies.items(), key=lambda item: item[1], reverse=True))

    return sorted_frequencies

if __name__ == "__main__":
    # Пример текста
    # text = input("Введите текст для анализа: ")

    text = """
    
собака съела товар и улетела в космос! 123 !"№ в течение

    """

    # Получение нормализованных частот функции слов
    frequencies = compute_function_word_frequencies(text)

    # Вывод результатов
    print("\n* Нормализованные частоты однотокенных функциональных слов:\n")
    for word, freq in frequencies.items():
        print(f"   '{word}': {freq:.2f}%")
# print(compute_function_word_frequencies(text))