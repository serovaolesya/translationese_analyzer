# import re
# from collections import defaultdict, Counter
# import pymorphy2
# from nltk.corpus import stopwords
#
# from custom_punkt_tokenizer import sent_tokenize_with_abbr
# from data import conjunctions, discource_markers, particles, prepositions, pronouns
# from tools.text_preparation import TextPreProcessor
#
# # Загрузка стоп-слов
# nltk_stopwords_ru = stopwords.words("russian")
#
# # 1. Объединение всех списков в один
# all_stopwords = set(conjunctions.conjunctions_list + prepositions.prepositions_list
#                     + particles.particles_list + pronouns.pronouns_list + nltk_stopwords_ru)
#
# # 2. Сортировка по длине по убыванию
# all_stopwords_sorted = sorted(list(all_stopwords), key=len, reverse=True)
#
# # Инициализация морфологического анализатора
# morph = pymorphy2.MorphAnalyzer()
#
# # Функция для получения POS-тегов с использованием pymorphy2
# def get_pos(word):
#     if re.match(r'[.!?]', word):  # Проверка на конечный знак препинания
#         return 'FINAL_PNCT'
#     if re.match(r'[,]', word):  # Проверка на запятую
#         return 'COMMA'
#     if re.match(r'[;]', word):  # Проверка на точку с запятой
#         return 'SEMICOLON'
#     if re.match(r'[:]', word):  # Проверка на двоеточие
#         return 'COLON'
#     parsed = morph.parse(word)[0]
#     return parsed.tag.POS
#
# def contextual_function_words(text):
#     text_processor = TextPreProcessor()
#     sentences = sent_tokenize_with_abbr(text)
#     func_words_contexts = defaultdict(list)
#     trigram_counter = Counter()
#     pos_trigram_counter = Counter()
#
#     for sent in sentences:
#         # Предварительная обработка текста
#         sent = text_processor.process_text(sent)
#
#         # Разделение слов и знаков препинания пробелами
#         sent = re.sub(r'([.,!?;])', r' \1 ', sent)  # Пробелы вокруг знаков препинания
#
#         # Удаление нежелательных символов
#         sent = re.sub(r'[^а-яА-ЯёЁA-Za-z0-9\s.,!?;]', '', sent)
#
#         # Токенизация предложения
#         tokens = sent.strip().split()
#
#         # Поиск триграмм
#         for i in range(len(tokens) - 2):
#             trigram = tokens[i:i + 3]  # Извлекаем триграмму
#
#             # Проверяем, содержит ли триграмма либо три стоп-слова, либо два стоп-слова и одно другое слово
#             stopword_count = sum(1 for word in trigram if word in all_stopwords)
#             if stopword_count == 3 or (stopword_count == 2 and any(word not in all_stopwords for word in trigram)):
#                 # Если триграмма соответствует условию, определяем POS-теги
#                 pos_trigram = [get_pos(word) if word in all_stopwords else get_pos(word) for word in trigram]
#                 trigram_str = ' '.join(trigram)
#                 func_words_contexts[trigram_str].append((trigram, pos_trigram))
#                 trigram_counter[tuple(trigram)] += 1
#                 pos_trigram_counter[tuple(pos_trigram)] += 1
#
#     print(trigram_counter)
#     print(pos_trigram_counter)
#     return func_words_contexts
#
# if __name__ == "__main__":
#     text = input("Введите текст для анализа:")
#     func_words_contexts = contextual_function_words(text)
#
#     print("Контексты стоп-слов и их части речи:")
#     for stopword, contexts in func_words_contexts.items():
#         print(f"\nСтоп-слово: '{stopword}'")
#         for trigram, pos_tags in contexts:
#             # Вывод полной информации о частях речи
#             print(f"  Триграмма: {trigram} - Части речи: {[str(tag) if tag is not None else None for tag in pos_tags]}")
