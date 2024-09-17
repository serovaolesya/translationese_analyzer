# -*- coding: utf-8 -*- # Языковая кодировка UTF-8
import random
import os
import re

from colorama import Style, Fore
from nltk import word_tokenize
from rich.console import Console

from tools.core.custom_punkt_tokenizer import sent_tokenize_with_abbr
from tools.core.text_preparation import TextPreProcessor
from tools.core.utils import wait_for_enter_to_analyze, wait_for_enter_to_choose_opt

console = Console()


def remove_links(text):
    """Удаляет ссылки и форматирует текст."""
    # Удаление ссылок (любой последовательности, начинающейся с http или www)
    text_without_links = re.sub(r'\(https?://\S+|www\.\S+\)', '', text)

    # Удаление простых сносок на литературу, например, [1]
    text_without_simple_references = re.sub(r'\s*\[\d+\]\s*', '', text_without_links)

    # Удаление сложных сносок на литературу, например, [1, 2], [1-3], [1; 2]
    text_without_complex_references_square_br = re.sub(r'\s*\[\d+((,\s*\d+)|([–-]\d+)|;\s*\d+)+\]\s*', '',
                                                       text_without_simple_references)

    # Удаление сложных сносок на литературу, например, (1, 2), (1-3), (1; 2)
    text_without_complex_references_round_br = re.sub(r'\s*\(\d+((,\s*\d+)|([–-]\d+)|;\s*\d+)+\)\s*', '',
                                                      text_without_complex_references_square_br)

    # Удаление ссылок, начинающихся на ( и содержащих год (четыре цифры) и оканчивающихся на )
    text_without_round_bracket_references = re.sub(r'\([^\)]*\b\d{4}\b[^\)]*\)', '',
                                                   text_without_complex_references_round_br)

    # Удаление ссылок, начинающихся на [ и содержащих год (четыре цифры) и оканчивающихся на ]
    text_without_square_bracket_references = re.sub(r'\[[^\)]*\b\d{4}\b[^\)]*\]', '',
                                                    text_without_round_bracket_references)

    # Удаление ссылок, начинающихся на ( или [ и содержащих 'с.' и заканчивающихся на ) или ]
    text_without_references_with_rus_page_1 = re.sub(r'[\[\(][^\]\)]+[сc]\.[^\]\)]+[\]\)]', '',
                                                     text_without_square_bracket_references)

    text_without_references_with_rus_page_2 = re.sub(r'\[\s*с\.\s*\d+\s*\]|\(\s*с\.\s*\d+\s*\)', '',
                                                     text_without_references_with_rus_page_1)

    # Замена двух и более пробелов на одинарный
    text_without_double_spaces = re.sub(r'\s{2,}', ' ', text_without_references_with_rus_page_2)

    # Удаляем красные строки (абзацы)
    text_without_newlines = text_without_double_spaces.replace('\n', ' ')

    # Удаление лишних пробелов в начале и конце текста
    text_without_extraendspaces = text_without_newlines.strip()

    # Удаление лишних пробелов перед пунктуацией (например, перед точкой)
    text_without_spaces_before_punct = re.sub(r'\s([?.!,":;])', r'\1', text_without_extraendspaces)

    # Удаляем повторяющиеся пунктуационные знаки
    text_without_repeated_punct = re.sub(r'(\W\s*)\1+', r'\1', text_without_spaces_before_punct)

    # Замена дефиса, окруженного пробелами, на длинное тире, окруженное пробелами
    text_without_hyphens = re.sub(r' \- ', ' — ', text_without_repeated_punct)
    print(
        Fore.LIGHTYELLOW_EX + Style.BRIGHT + "\nУДАЛЕНИЕ ССЫЛОК ИЗ ТЕКСТА УСПЕШНО ЗАВЕРШЕНО" + Fore.RESET)

    return text_without_hyphens


def show_sent_tokenization(sentences):
    """
     Показывает предложения с указанием их индексов, а также первого и последних двух токенов.

     :param sentences: Список предложений.
     """
    for index, sent in enumerate(sentences, start=1):
        words = word_tokenize(sent)
        first_token = words[0] if words else ''
        last_but_one_token = words[-2] if words else ''
        last_token = words[-1] if words else ''
        print(
            Fore.LIGHTWHITE_EX + Style.BRIGHT + f" {index})" + Fore.LIGHTBLUE_EX + f" [{first_token}, {last_but_one_token} {last_token}]" + Fore.LIGHTWHITE_EX + Style.NORMAL + f" {sent}")


def adjust_text_length(text):
    """
    Подгоняет текст под заданное количество предложений.

    :param text: Входной текст.
    :return str: Отредактированный текст с указанным количеством предложений.
    """
    print(
        Fore.LIGHTYELLOW_EX + Style.BRIGHT + "ВЫРАВНИВАНИЕ ТЕКСТА ПО ДЛИНЕ ЗАПУЩЕНО\n" + Fore.RESET)
    while True:
        try:
            target_sentence_count = int(
                input(Fore.LIGHTYELLOW_EX + Style.BRIGHT + "Введите желаемое количество предложений: \n" + Fore.RESET))
            if target_sentence_count > 0:
                break
            else:
                print(Fore.LIGHTRED_EX + "Число предложений должно быть больше нуля.\n" + Fore.RESET)
        except ValueError:
            print(Fore.LIGHTRED_EX + "Пожалуйста, введите целое число.\n" + Fore.RESET)

    text_processor = TextPreProcessor()
    text_spacing_fixed = text_processor.fix_spacing_for_mean_sent_len(text)
    sentences = sent_tokenize_with_abbr(text)
    current_sentence_count = len(sentences)
    if current_sentence_count < target_sentence_count:
        print(
            Fore.LIGHTRED_EX + Style.BRIGHT + f"Введенный текст содержит {current_sentence_count} предложений(я), желаемая"
                                              f" длина текста составляет {target_sentence_count} предложений(я)."
                                              f"\nПожалуйста, либо выберите текст большей длины, и либо измените требуемое "
                                              f"количество предложений.\nРезультаты удаления ссылок будут сохранены!" + Fore.RESET)
        wait_for_enter_to_analyze()
        return text
    print(Fore.LIGHTGREEN_EX + Style.BRIGHT + "\nПеред выравниванием текста по длине, пожалуйста, проверьте "
                                              "правильность автоматического разбиения\nтекста на предложения, "
                                              "так как это может повлиять на результат." + Fore.RESET)
    wait_for_enter_to_analyze()
    print(
        Fore.LIGHTRED_EX + Style.BRIGHT + "\nВНИМАНИЕ!\n"
        + Fore.LIGHTGREEN_EX + Style.BRIGHT + "Далее для удобства проверки перед каждым предложением в скобках будет "
                                      "выведена информация о\nпервом и двух последних токенах в предложении. "
                                      "Первый токен должен совпасть с началом предложения,\nпоследние два - с последним"
                                      " словом предложения и финальным знаком препинания соответственно." + Fore.RESET)
    wait_for_enter_to_analyze()
    print(
        Fore.LIGHTYELLOW_EX + Style.BRIGHT + "\nПожалуйста, внимательно просмотрите разбивку"
                                             " и удостоверьтесь в ее правильности:" + Fore.RESET)
    wait_for_enter_to_analyze()
    show_sent_tokenization(sentences)
    while True:
        response = input(
            Fore.LIGHTYELLOW_EX + Style.BRIGHT + "\nТекст разбит на предложения правильно (y/n)?\n" + Fore.RESET).strip().lower()
        if response in ['y', 'n']:
            break
        else:
            print(
                Fore.LIGHTRED_EX + Style.BRIGHT + "Неправильный выбор. Пожалуйста, введите один из"
                                                  " предложенных вариантов (y/n)." + Fore.RESET)

    if response == 'n':
        print(
            Fore.LIGHTRED_EX + Style.BRIGHT + "Пожалуйста, для выравнивания текста по длине отредактируйте"
                                              " текст вручную и перезапустите процесс.\nРезультаты удаления"
                                              " ссылок будут сохранены!" + Fore.RESET)
        wait_for_enter_to_analyze()
        return text

    if response == 'y':
        if current_sentence_count == target_sentence_count:
            print(
                Fore.LIGHTRED_EX + Style.BRIGHT + f"Введенный текст уже содержит требуемое количество"
                                                  f" предложений ({target_sentence_count})." + Fore.RESET)
            wait_for_enter_to_analyze()
            return text

        while len(sentences) != target_sentence_count:
            print(
                Fore.LIGHTGREEN_EX + Style.BRIGHT + f"\nТекущая длина текста: {len(sentences)}"
                                                    f" предложений, целевая длина: {target_sentence_count}." + Fore.RESET)

            action = input(
                Fore.LIGHTYELLOW_EX + Style.BRIGHT + "\nВыберите действие:" + Fore.LIGHTWHITE_EX +
                Style.BRIGHT + "\n1) Удалить предложения случайным образом " +
                Fore.LIGHTGREEN_EX + Style.BRIGHT + "(рекомендовано)" + Fore.LIGHTWHITE_EX
                + Style.BRIGHT + "\n2) Выбрать предложения для удаления по индексу"
                + Fore.LIGHTYELLOW_EX + Style.BRIGHT + "\nВведите номер действия:\n" + Fore.RESET).strip()

            if action == '1':
                if target_sentence_count < current_sentence_count:
                    indices_to_remove = random.sample(range(current_sentence_count),
                                                      current_sentence_count - target_sentence_count)
                    sentences = [sent for i, sent in enumerate(sentences) if i not in indices_to_remove]
                    print(
                        Fore.LIGHTGREEN_EX + Style.BRIGHT + "\nОбновленный список предложений после удаления:" + Fore.RESET)
            elif action == '2':
                while len(sentences) != target_sentence_count:
                    try:
                        current_sentence_count = len(sentences)
                        remaining_to_remove = current_sentence_count - target_sentence_count

                        indices_to_remove = input(Fore.LIGHTYELLOW_EX + Style.BRIGHT +
                                                  f"Введите номера предложений для удаления (в диапазоне 1-{current_sentence_count}), "
                                                  f"разделенные пробелами. Максимум можно удалить {remaining_to_remove} предложений:\n" + Fore.RESET).strip()

                        indices_to_remove = list(map(int, indices_to_remove.split()))

                        # Проверка, чтобы количество удаляемых предложений не превышало необходимое для достижения целевой длины
                        if len(indices_to_remove) > remaining_to_remove:
                            print(Fore.LIGHTRED_EX + Style.BRIGHT +
                                  f"Вы пытаетесь удалить слишком много предложений. Можно удалить только {remaining_to_remove}.\n" + Fore.RESET)
                            continue

                        if all(1 <= idx <= current_sentence_count for idx in indices_to_remove):
                            sentences = [sent for i, sent in enumerate(sentences) if i + 1 not in indices_to_remove]
                            print(
                                Fore.LIGHTGREEN_EX + Style.BRIGHT + "\nОбновленный список предложений после удаления:" + Fore.RESET)
                            show_sent_tokenization(sentences)
                            print(
                                Fore.LIGHTGREEN_EX + Style.BRIGHT + f"Текущая длина текста: {len(sentences)} предложений, "
                                                                    f"целевая длина: {target_sentence_count}." + Fore.RESET)

                            if len(sentences) == target_sentence_count:
                                break  # Выходим из цикла, если достигли нужной длины
                        else:
                            print(
                                Fore.LIGHTRED_EX + Style.BRIGHT + f"Пожалуйста, введите номера в диапазоне от 1 до "
                                                                  f"{current_sentence_count}." + Fore.RESET)
                    except ValueError:
                        print(Fore.LIGHTRED_EX + Style.BRIGHT + "Введите корректные числовые значения." + Fore.RESET)

            else:
                print(
                    Fore.LIGHTRED_EX + Style.BRIGHT + "Неверный ввод. Пожалуйста, выберите один из предложенных вариантов." + Fore.RESET)

        if len(sentences) == target_sentence_count:
            show_sent_tokenization(sentences)
            new_text = ' '.join(sentences)
            print(
                Fore.LIGHTGREEN_EX + Style.BRIGHT + f"\nЦелевое количество предложений достигнуто ({target_sentence_count})!\n" + Fore.RESET)
            wait_for_enter_to_analyze()
            return new_text


def process_text_from_file(file_path, init_dir):
    """Обрабатывает текст из файла и сохраняет результат."""
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()
    cleaned_text = remove_links(text)
    wait_for_enter_to_analyze()
    length_adjusted_text = adjust_text_length(cleaned_text)

    # Выбор места сохранения
    if init_dir == '1':
        save_directory = "auth_ready/"
        folder_name = "'auth_ready'"
    if init_dir == '2':
        save_directory = "mt_ready/"
        folder_name = "'mt_ready'"
    if init_dir == '3':
        save_directory = "ht_ready/"
        folder_name = "'ht_ready'"

    os.makedirs(save_directory, exist_ok=True)

    # Формирование нового имени файла
    dir_name, base_name = os.path.split(file_path)
    name, extension = os.path.splitext(base_name)
    new_file_name = f"{name}_processed{extension}"
    new_file_path = os.path.join(save_directory, new_file_name)

    with open(new_file_path, 'w', encoding='utf-8') as file:
        file.write(length_adjusted_text)

    print(
        Fore.LIGHTGREEN_EX + Style.BRIGHT + f"\nРезультат успешно сохранен! "
                                            f"Вы можете найти его в папке "
                                            f"{folder_name} (она находится в корневой директории)." + Fore.RESET)
    print(
        Fore.LIGHTRED_EX + Style.BRIGHT + f"Для дальнейшего анализа текста скопируйте текст из файла. "
                                          f"При необходимости отредактируйте его вручную.\n" + Fore.RESET)
    wait_for_enter_to_choose_opt()


def main():
    print("\n" + Fore.LIGHTWHITE_EX + "*" * 100)
    print(
        Fore.LIGHTYELLOW_EX + Style.BRIGHT + "                     ПРОЦЕСС ПОДГОТОВКИ ТЕКСТА К ДАЛЬНЕЙШЕМУ АНАЛИЗУ ЗАПУЩЕН" + Fore.RESET)
    print(Fore.LIGHTWHITE_EX + "*" * 100)

    while True:
        mode = input(
            Fore.LIGHTYELLOW_EX + Style.BRIGHT + "Введите 'f' для обработки файла или 't' для ввода текста вручную: " + Fore.RESET).strip().lower()

        if mode.lower().strip() == 'f':
            while True:
                print(
                    Fore.LIGHTYELLOW_EX + Style.BRIGHT + "\nВыберите директорию с Вашим текстовым файлом (.txt)." + Fore.RESET)
                print(Fore.LIGHTWHITE_EX + "1. Директория с аутентичными текстами /auth_texts/")
                print(Fore.LIGHTWHITE_EX + "2. Директория с машинными переводами /mt_texts/")
                print(Fore.LIGHTWHITE_EX + "3. Директория с переводами, сделанными человеком /ht_texts/")
                dir_choice = input(
                    Fore.LIGHTYELLOW_EX + Style.BRIGHT + "Введите номер директории: " + Fore.RESET).strip()

                if dir_choice == '1':
                    directory = "auth_texts/"
                elif dir_choice == '2':
                    directory = "mt_texts/"
                elif dir_choice == '3':
                    directory = "ht_texts/"
                else:
                    print(Fore.LIGHTRED_EX + Style.BRIGHT + "\nНеверный выбор. Попробуйте снова." + Fore.RESET)
                    continue

                file_name = input(Fore.LIGHTYELLOW_EX + "Введите название файла в"
                                                        " выбранной директории "
                                                        "(только файлы .txt): " + Fore.RESET).strip()
                file_path = directory + file_name + '.txt'
                if os.path.isfile(file_path):
                    process_text_from_file(file_path, dir_choice)
                    break
                else:
                    print(
                        Fore.LIGHTRED_EX + Style.BRIGHT + "Файл не найден. Проверьте путь и попробуйте снова." + Fore.RESET)
                continue

        elif mode.lower().strip() == 't':
            while True:
                print(Fore.LIGHTYELLOW_EX + Style.BRIGHT + "\nВыберите тип текста." + Fore.RESET)
                print(Fore.LIGHTWHITE_EX + Style.BRIGHT + "1. Аутентичный текст")
                print(Fore.LIGHTWHITE_EX + Style.BRIGHT + "2. Машинный перевод")
                print(Fore.LIGHTWHITE_EX + Style.BRIGHT + "3. Перевод, сделанный человеком")
                text_type_choice = input(
                    Fore.LIGHTRED_EX + Style.BRIGHT + "Введите номер типа текста: " + Fore.RESET).strip()

                # Выбор места сохранения
                if text_type_choice == '1':
                    save_directory = "auth_ready/"
                    folder_name = "'auth_ready'"
                elif text_type_choice == '2':
                    save_directory = "mt_ready/"
                    folder_name = "'mt_ready'"
                elif text_type_choice == '3':
                    save_directory = "ht_ready/"
                    folder_name = "'ht_ready'"
                else:
                    print(Fore.LIGHTRED_EX + Style.BRIGHT + "Неверный выбор. Попробуйте снова." + Fore.RESET)
                    continue
                # Ввод текста вручную
                text = get_full_input()
                # Формирование имени файла для сохранения
                file_name = input(
                    Fore.LIGHTYELLOW_EX + Style.BRIGHT + "Введите имя файла для сохранения "
                                                         "результата (без расширения): " + Fore.RESET).strip()

                # Создание папки для сохранения, если её нет
                os.makedirs(save_directory, exist_ok=True)

                file_path = os.path.join(save_directory, f"{file_name}_processed.txt")

                cleaned_text = remove_links(text)
                wait_for_enter_to_analyze()
                length_adjusted_text = adjust_text_length(cleaned_text)

                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(length_adjusted_text)

                print(
                    Fore.LIGHTGREEN_EX + Style.BRIGHT + f"\nРезультат успешно сохранен! "
                                                        f"Вы можете найти его в папке {folder_name} "
                                                        f"(она находится в корневой директории)." + Fore.RESET)
                print(
                    Fore.LIGHTRED_EX + Style.BRIGHT + f"Для дальнейшего анализа текста скопируйте текст из файла. "
                                                      f"При необходимости отредактируйте его вручную.\n" + Fore.RESET)

                break
            wait_for_enter_to_choose_opt()
            break
        else:
            print(Fore.LIGHTRED_EX + Style.BRIGHT + "Неверный выбор. Попробуйте снова." + Fore.RESET)
        break


def get_full_input():
    print(Fore.LIGHTYELLOW_EX + Style.BRIGHT + "\nВведите текст для анализа (по окончанию ввода с красной строки"
                                       " напечатайте 'r' и нажмите 'Enter'):" + Fore.RESET)
    input_lines = []
    while True:
        line = input()
        if line.lower().strip() == "r":
            break
        input_lines.append(line)
    return '\n'.join(input_lines)

