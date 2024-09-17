# -*- coding: utf-8 -*- # Языковая кодировка UTF-8
import re

# from ruwordnet import RuWordNet
#
# wn = RuWordNet()
#
# # # Можно искать синсеты, в которые входит слово
# # for sense in wn.get_senses('замок'):
# #     print(sense.synset)
# #
# # # Для каждого синсета можно глядеть на гиперонимы...
# # asparagus_hyper = wn.get_senses('спаржа')[0].synset.hypernyms[0]
# # print(asparagus_hyper)
# #
# # # ... или, наоборот, на гипонимы
# # print(asparagus_hyper.hyponyms)
# #
# # print(wn.get_senses('авокадо'))
# #
# # print(wn['153966-N-124560'])
# #
# # print(wn.get_senses('потенциал')
# # )
#
#
# rwn = RuWordNet()
#
#
# def get_synonyms(word):
#     """Получает синонимы слова."""
#     synsets = rwn.get_synsets(word)
#     synonyms = set()
#     for synset in synsets:
#         for sense in synset.senses:
#             synonyms.update(sense.words)
#     return synonyms
#
#
# # word = 'дерево'
# # synonyms = get_synonyms(word)
# # print(f"Синонимы слова '{word}': {synonyms}")
#
#
# def print_synset_details(word):
#     """
#     Получает и выводит детали о синсетах для заданного слова.
#
#     Параметры:
#     word (str): Слово, для которого нужно получить информацию о синсетах.
#     """
#     # Получаем синсеты (смысловые группы) для заданного слова
#     synsets = rwn.get_synsets(word)
#
#     # Выводим информацию о каждом синсете
#     print(f"\nSynsets for the word '{word}':")
#     for synset in synsets:
#         print(f"\nSynset ID: {synset.id}")  # ID синсета
#
#         # Проверяем, есть ли смыслы в синсете
#         if synset.senses:
#             print("Senses:")
#             for sense in synset.senses:
#                 # Проверяем, есть ли слова в смысле
#                 if sense.words:
#                     # Для каждого смысла выводим ID и связанные слова
#                     print(f"  Sense ID: {sense.id}, Words: {', '.join(word.name for word in sense.words)}")
#                 else:
#                     # Если слова отсутствуют
#                     print(f"  Sense ID: {sense.id}, Words: No words available")
#         else:
#             # Если смыслы отсутствуют
#             print("No senses available in this synset")
#
#
# def get_hypernyms(word):
#     """Получает гиперонимы слова."""
#     synsets = rwn.get_synsets(word)
#     hypernyms = set()
#     for synset in synsets:
#         for hypernym in synset.hypernyms:
#             hypernyms.update(hypernym.senses)
#     return hypernyms
#
#
#
# def get_hyponyms(word):
#     """Получает гипонимы слова."""
#     synsets = rwn.get_synsets(word)
#     hyponyms = set()
#     for synset in synsets:
#         for hyponym in synset.hyponyms:
#             hyponyms.update(hyponym.senses)
#     return hyponyms
#
#
# # Пример использования
# word = 'красотка'
# # print_synset_details(word)
#
#
# # print(get_synonyms(word))
# # print(get_hyponyms(word))
#
# # Вывод доменов (областей применения) для слова 'мяч'
# print(wn['мяч'][0].synset.domains)
# # Цель: Показать области применения (domains), к которым относится понятие "мяч".
# # Это может включать такие области, как "спорт" или "игра".
#
# # Вывод элементов домена (атрибутов) для слова 'спорт'
# print(wn['спорт'][0].synset.domain_items)
# # Цель: Показать элементы домена (domain_items), связанные с понятием "спорт".
# # Это может включать конкретные предметы или атрибуты, относящиеся к спорту, например, "мяч".
#
# # Вывод холонимов (целых объектов, к которым относится часть) для слова 'нос'
# print(wn['нос'][0].synset.holonyms)
# # Цель: Показать холонимы (holonyms), связанные с понятием "нос".
# # Это могут быть целые объекты, частью которых является "нос", например, "человек".
#
# # Вывод меронимов (частей целого) для слова 'дерево'
# print(wn['дерево'][0].synset.meronyms)
# # Цель: Показать меронимы (meronyms), связанные с понятием "дерево".
# # Это могут быть части дерева, такие как "ветка" или "листья".
#
# # Вывод классов (обобщенных категорий) для слова 'Москва'
# print(wn['Москва'][0].synset.classes)
# # Цель: Показать классы (classes), к которым относится понятие "Москва".
# # Это могут быть более общие категории, такие как "город" или "столица".
#
# # Вывод экземпляров (конкретных объектов) для слова 'областной центр'
# print(wn['областной центр'][0].synset.instances)
# # Цель: Показать экземпляры (instances) понятия "областной центр".
# # Это могут быть конкретные примеры областных центров, например, "Москва" или "Казань".
#
# # Вывод антонимов для слова 'здоровье'
# print(wn['здоровье'][0].synset.antonyms)
# # Цель: Показать антонимы (antonyms) понятия "здоровье".
# # Это могут быть слова, противоположные "здоровье", например, "болезнь".
#
# # Вывод связанных синсетов для слова 'спорт'
# print(wn['спорт'][0].synset.related)
# # Цель: Показать прочие смысловые связи (related) для понятия "спорт".
# # Это могут быть другие понятия, которые связаны с "спортом", например, "физкультура".
#
# # Вывод интерлингвальных индексов для слова 'дерево'
# print(wn['дерево'][0].synset.ili)
# # Цель: Показать интерлингвальные индексы (ili) для понятия "дерево".
# # Это могут быть эквиваленты понятия "дерево" в других языках, таких как английский.
#
# # Вывод фраз, содержащих слово 'спорт'
# print(wn['спорт'][0].phrases)
# # Цель: Показать фразы (phrases), содержащие слово "спорт".
# # Это могут быть выражения или сочетания слов, в которых используется "спорт", например, "гребной спорт".
#
# # Вывод слов, из которых состоит фраза для 'новый год'
# print(wn['новый год'][0].words)
# # Цель: Показать слова (words), из которых состоит фраза "новый год".
# # Это может быть полезно для понимания, как эта фраза формируется из отдельных слов.
#
# # Вывод дериваций (производных слов) для слова 'центр'
# print(wn['центр'][0].derivations)
# # Цель: Показать деривации (derivations) для понятия "центр".
# # Это могут быть слова, происходящие от "центр", например, "центровой" или "центральный".
#

import pymorphy2

morph = pymorphy2.MorphAnalyzer()



text = """

    крокозябра дутая, маная. я сломанный. risky cities использует «истории обучения» в качестве основы.
"""

text = re.sub(r'([\.\,\!\?\;\%\)\)\[\]\:\—])', r' \1 ', text)  # Разделяем знаки препинания пробелами

example = []
for token in text.split():
    token = token.strip()
    parsed_token = morph.parse(token)[0]
    example.append(parsed_token)
print(example)

# POS = PRTF, Case = Nom, Number = Sing, Gender = Masc, Aspect = Perf, Tense = Past, Voice = Passive