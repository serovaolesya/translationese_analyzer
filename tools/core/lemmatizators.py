# -*- coding: utf-8 -*- # Языковая кодировка UTF-8
import re

from nltk import word_tokenize
from nltk.corpus import stopwords
from pymorphy2 import MorphAnalyzer

from tools.core.custom_punkt_tokenizer import sent_tokenize_with_abbr
from tools.core.data import pronouns, prepositions, particles, conjunctions
from tools.core.text_preparation import TextPreProcessor

nltk_stopwords_ru = stopwords.words("russian")

# 1. Объединение всех списков в один
all_stopwords = set(conjunctions.conjunctions_list + prepositions.prepositions_list
                    + particles.particles_list + pronouns.pronouns_list + nltk_stopwords_ru)

# 2. Сортировка по длине по убыванию
all_stopwords_sorted = sorted(list(all_stopwords), key=len, reverse=True)


def remove_custom_stopwords(text):
    """
    Удаляет кастомные стоп-слова из текста.

    :param text: Входной текст, из которого необходимо удалить стоп-слова.
    :return: Текст без стоп-слов.
    """
    # Проходим по каждому стоп-слову и заменяем его в тексте, проверяя на границы слова
    for stopword in all_stopwords_sorted:
        # Используем re.sub для замены стоп-слов на пустую строку
        text = re.sub(r'(?<!-)\b' + re.escape(stopword) + r'\b(?!-)', '', text.lower())

    # Убираем лишние пробелы после удаления стоп-слов
    text = re.sub(r'\s+', ' ', text).strip()

    return text


# patterns = "[A-Za-z0-9!#$%&'()*+,./:;<=>?@[\]^_`{|}~—\"”“]
patterns = r"[^А-Яа-яёЁ\-]+"  # Оставляем только кириллицу и дефис

morph = MorphAnalyzer()


def lemmatize_words_without_stopwords(text, patterns):
    """
    Лемматизирует слова в тексте после удаления кастомных стоп-слов.

    :param text: Входной текст на русском языке.
    :param patterns: Регулярное выражение для фильтрации токенов.
    :return: Список объектов Parse, содержащих информацию о каждом токене.
    """
    text = remove_custom_stopwords(text)
    text = re.sub(patterns, ' ', text)
    tokens_full_info = []
    for token in text.split():
        token = token.strip()
        token = morph.parse(token)[0]
        tokens_full_info.append(token)
    return tokens_full_info


def lemmatize_words(text):
    """
    Лемматизирует слова в тексте, оставляя только кириллицу и дефис.

    :param text: Входной текст на русском языке.
    :return: Список объектов Parse, содержащих информацию о каждом токене.
    """
    text = re.sub(patterns, ' ', text)
    # Предобработка текста: замена аббревиатур и исправление пробелов
    text_processor = TextPreProcessor()
    text = text_processor.fix_spacing(text)

    tokens_full_info = []
    for token in text.split():
        token = token.strip()
        # print(token)
        token = morph.parse(token)[0]
        tokens_full_info.append(token)
    return tokens_full_info


def lemmatize_words_into_sents_for_pmi(text):
    """
     Разбивает текст на предложения, токенизирует их, лемматизирует и возвращает список предложений,
     где каждое предложение представлено списком лемматизированных токенов.
     Остаются только словарные токены, предназначено для подсчета PMI.

     :param text: Входной текст на русском языке.
     :return: Список предложений, каждое из которых является списком лемматизированных токенов.
     """
    # Очистка текста от лишних символов, кроме знаков препинания (для токенизации по предложениям) и кириллических букв
    text = re.sub(r'[^а-яА-ЯёЁ\s\.\!\?]', '', text)
    sentences = sent_tokenize_with_abbr(text)
    lemmatized_sentences = []
    for sentence in sentences:
        tokens = word_tokenize(sentence, language="russian")  # Токенизируем предложение на слова
        lemmatized_tokens = [morph.parse(token)[0].normal_form for token in tokens if
                             token not in ['.', '?', '!']]  # Лемматизируем токены и фильтруем знаки препинания
        lemmatized_sentences.append(lemmatized_tokens)

    return lemmatized_sentences


def lemmatize_words_into_sents_for_n_grams(text):
    """
    Разбивает текст на предложения, токенизирует их, лемматизирует и возвращает список предложений,
    где каждое предложение представлено списком лемматизированных токенов и их частей речи.

    :param text: Входной текст на русском языке.
    :return: Кортеж из двух списков:
        - tokens_pos: Список токенов с метками частей речи и специальными маркерами для начала и конца предложений.
        - lemmas: Список лемматизированных токенов.
    """
    # Разделяем слова и знаки препинания пробелами
    text = re.sub(r'([\.\,\!\?\;\%\)\)\[\]\:\—])', r' \1 ', text)
    # Очистка текста от лишних символов, кроме знаков препинания (для токенизации по предложениям) и кириллических букв
    text = re.sub(r'[^а-яА-ЯёЁ\s\.\!\?\,\-]', '', text)
    tokens_pos = []
    lemmas = []
    previous_token = None
    for token in text.split():
        token = token.strip()
        parsed_token = morph.parse(token)[0]
        # Обработка конца предложения
        if previous_token and previous_token in '!?.]' and token[0].isupper():
            tokens_pos.append('S_START')

        if parsed_token.tag.POS:
            tokens_pos.append(parsed_token.tag.POS)
            lemmas.append(parsed_token.normal_form)
        if parsed_token.normal_form in '!?.]':
            tokens_pos.append('S_END')
            lemmas.append(parsed_token.normal_form)
        if parsed_token.normal_form in ',':
            tokens_pos.append('COMMA')
            lemmas.append(parsed_token.normal_form)
        previous_token = parsed_token.normal_form

    return tokens_pos, lemmas


if __name__ == "__main__":
    # Текст для примера (сгенерирован ИИ)
    text = """В старом доме на окраине города жила семья, которая была известна своей гостеприимностью. Дом был 
    построен много лет назад и был окружен большим садом, который был засажен цветами и деревьями. Семья была любима 
    всеми соседями, и к ней часто приходили гости. Семья была большая, и в ней было много детей, которые всегда 
    играли во дворе. Дети были веселыми и любопытными, и они всегда находили что-то интересное, чтобы сделать. Они 
    были окружены любящими родителями, которые всегда заботились о них. Отец семьи был известным художником, 
    и он часто писал картины, которые были выставлены в местных галереях. Мать была отличной поварихой, и она всегда 
    готовила вкусные блюда, которые были любимы всеми. Дети были учениками местной школы, и они всегда получали 
    хорошие оценки. В доме часто проводились вечеринки, на которые приходили друзья и соседи. Вечеринки были всегда 
    веселыми, и все гости всегда уходили с улыбками на лицах. Семья была счастлива и гармонична, и все члены семьи 
    любили друг друга. Дом был полон книг, и все члены семьи любили читать. Они часто сидели в библиотеке и читали 
    книги, которые были написаны известными авторами. Семья была любима всеми, и к ней всегда приходили гости."""

    a = lemmatize_words_without_stopwords(text, patterns)
    b = lemmatize_words(text)
    c = lemmatize_words_into_sents_for_n_grams(text)
    d = lemmatize_words_into_sents_for_pmi(text)

    print(a)
    print()

    print(b)
    print()

    print(c)
    print()

    print(d)
