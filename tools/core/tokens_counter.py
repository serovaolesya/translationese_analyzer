import re

import re

import re


def separate_tokens_with_hyphen(text):
    """
    Отделяет буквенные токены от символов пунктуации, за исключением дефиса, который остается частью слов.

    :param text: Строка текста для обработки.
    :return: Строка с отделенными буквенными токенами и символами пунктуации (кроме дефиса).
    """
    # Регулярное выражение для разделения буквенных токенов и символов пунктуации, исключая дефис внутри слов
    separated_text = re.sub(r'(\w+)([^\w\s-])', r'\1 \2', text)  # отделяет пунктуацию, но оставляет дефис
    separated_text = re.sub(r'([^\w\s-])(\w+)', r'\1 \2',
                            separated_text)  # разделяет пунктуацию перед словами, кроме дефиса
    separated_text = re.sub(r'(\s)-(\s)', r'\1-\2', separated_text)  # оставляет дефисы в середине слов
    return separated_text


def count_tokens(text):
    """
    Подсчитывает общее количество токенов в тексте, состоящих из кириллицы, латиницы и дефиса.

    :param text: Строка текста для анализа.
    :return: Количество токенов, состоящих из кириллицы, латиницы и дефиса.
    """
    # Регулярное выражение для токенов, содержащих только кириллицу, латиницу или дефисы
    pattern = r'\b[А-Яа-яЁёA-Za-z-]+\b'
    separated_text = separate_tokens_with_hyphen(text)
    # Поиск всех токенов по регулярному выражению
    alpha_tokens = re.findall(pattern, separated_text)

    # Подсчет количества токенов
    alpha_tokens_count = len(alpha_tokens)
    all_tokens = re.findall(r'\S+', separated_text)

    # Подсчет общего количества токенов
    all_tokens_count = len(all_tokens)

    all_punct_tokens_count = all_tokens_count - alpha_tokens_count

    return all_tokens_count, alpha_tokens_count, all_punct_tokens_count


if __name__ == "__main__":
    # Пример использования
    text = "Пример текста  русском языке! и  КАКОЙ-ТО text in English."
    all_tokens_count, alpha_tokens_count, all_punct_tokens_count = count_tokens(text)
    print(all_tokens_count)
    print(alpha_tokens_count)
    print(all_punct_tokens_count)

