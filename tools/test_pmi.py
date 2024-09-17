# -*- coding: utf-8 -*- # Языковая кодировка UTF-8
import os
import glob
import math
from collections import Counter

from tools.core.lemmatizators import lemmatize_words_into_sents_for_pmi


def read_texts_from_directory(directory):
    """Считывает все текстовые файлы из указанной директории и возвращает их содержимое в виде списка строк."""
    texts = []
    # Ищем все файлы с расширением .txt в указанной директории
    for filename in glob.glob(os.path.join(directory, '*.txt')):
        with open(filename, 'r', encoding='utf-8') as file:
            text = file.read()
            texts.append(text)
    return texts


def calculate_pmi_for_chunk(text):
    """Расчет PMI для корпуса текстов из указанной директории."""
    all_bigrams = Counter()  # Используем Counter для хранения и подсчета биграмм
    word_counts = Counter()  # Используем Counter для подсчета частоты слов

    # Лемматизация текста и получение полной информации по каждому слову
    lemmatized_sentences = lemmatize_words_into_sents_for_pmi(text)

    for sentence in lemmatized_sentences:
        word_counts.update(sentence)  # Обновляем счетчик частоты слов

        # Создание биграмм внутри предложения
        bigrams = zip(sentence[:-1], sentence[1:])
        all_bigrams.update(bigrams)  # Обновляем частоты биграмм

    total_word_number = sum(word_counts.values())

    # Вычисляем вероятности для слов и биграмм
    p_word = {word: count / total_word_number for word, count in word_counts.items()}
    p_bigram = {bigram: count / total_word_number for bigram, count in all_bigrams.items()}

    pmi_values = {}
    bigrams_above_zero = 0  # Счетчик биграмм с PMI > 0 (добавлено)

    for bigram, count in all_bigrams.items():
        w1, w2 = bigram
        pmi = math.log2(p_bigram[bigram] / (p_word[w1] * p_word[w2]))
        if pmi > 0:
            pmi_values[bigram] = pmi
            bigrams_above_zero += 1  # Увеличиваем счетчик биграмм с PMI > 0

    sorted_pmi_values = sorted(pmi_values.items(), key=lambda x: x[1], reverse=True)
    normalized_value = bigrams_above_zero / len(all_bigrams) if len(all_bigrams) > 0 else 0
    return dict(sorted_pmi_values), bigrams_above_zero, normalized_value


def calculate_pmi_for_corpus(corpus_directory):
    """Расчет PMI для корпуса текстов из указанной директории."""
    texts = read_texts_from_directory(corpus_directory)  # Чтение текстов в виде списка
    results = []  # Список для хранения результатов для каждого текста

    total_bigrams_above_zero = 0  # Сумма биграмм с PMI > 0 по всему корпусу (новое)
    total_bigrams_count = 0  # Общее количество биграмм по всему корпусу (новое)

    # Обработка каждого текста в корпусе по отдельности
    for text in texts:
        # Рассчитываем PMI для каждого текста (chunk)
        pmi_values, bigrams_above_zero, normalized_value = calculate_pmi_for_chunk(text)

        # Сохраняем результаты для каждого текста
        results.append((pmi_values, bigrams_above_zero, normalized_value))

        # Увеличиваем счетчики для всего корпуса (новое)
        total_bigrams_above_zero += bigrams_above_zero
        total_bigrams_count += len(pmi_values)

    # Расчет Threshold PMI для всего корпуса (новое)
    corpus_threshold_pmi = total_bigrams_above_zero / total_bigrams_count if total_bigrams_count > 0 else 0

    return results, corpus_threshold_pmi  # Возвращаем результаты и Threshold PMI для корпуса


directory = '../auth_texts'
results, corpus_threshold_pmi = calculate_pmi_for_corpus(directory)  # Получаем результаты и Threshold PMI для всего корпуса

# Итерация по результатам и вывод данных для каждого текста (chunk)
for i, (pmi_values, bigrams_above_zero, normalized_value) in enumerate(results, start=1):
    print(f"Text {i}:")
    for index, (bigram, pmi) in enumerate(pmi_values.items(), start=1):
        print(f"{index}. Bigram: {bigram}, PMI: {pmi:.4f}")
    print(f'\nНайдено {bigrams_above_zero} биграмов с PMI > 0.')
    print(f'Нормализованное значение: {normalized_value:.4f}\n')

# Вывод Threshold PMI для всего корпуса (новое)
print(f'\nThreshold PMI для всего корпуса: {corpus_threshold_pmi:.4f}')
# 44191 Аут из 45129
# 42849 МП

# if __name__ == "__main__":
#     directory = '../test_texts'
#     pmi_values, above_zero = calculate_pmi(directory)
#
#     for index, (bigram, pmi) in enumerate(pmi_values.items(), start=1):
#         print(f"{index}. Bigram: {bigram}, PMI: {pmi:.4f}")
#     print(f'\nНайдено {above_zero} биграмов с PMI>0.')
