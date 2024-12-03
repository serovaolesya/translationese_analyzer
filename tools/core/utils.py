import os

from colorama import Fore, Style
from natasha import (Segmenter,
                     MorphVocab,

                     NewsEmbedding,
                     NewsMorphTagger,
                     NewsSyntaxParser,
                     NewsNERTagger,

                     PER,
                     NamesExtractor,

                     Doc
                     )
from prettytable import PrettyTable
from rich.console import Console
from rich.table import Table

from tools.core.constants import GRAMMEMES_MORPH_ANNOTATION_GRAM_CATEGORIES, GRAMMEMES_NGRAMS, \
    GRAMMEMES_MORPH_ANNOTATION, NON_TRANSLATED_DB_NAME, MACHINE_TRANSLATED_DB_NAME, HUMAN_TRANSLATED_DB_NAME

console = Console()


def wait_for_enter_to_analyze():
    """Функция, которая ждет нажатия Enter, чтобы продолжить анализ."""
    while True:
        pause = input(Fore.LIGHTBLUE_EX + Style.BRIGHT + "Нажмите 'Enter', чтобы продолжить." + Fore.RESET)
        if pause.strip() == '':  # если нажали только Enter (строка пустая)
            break


def wait_for_enter_to_choose_opt():
    """
     Ожидает нажатия клавиши Enter от пользователя, чтобы вернуться к выбору опции.
     """
    while True:
        pause = input(
            Fore.LIGHTBLUE_EX + Style.BRIGHT + "Нажмите 'Enter', чтобы вернуться к выбору опции." + Fore.RESET)
        if pause.strip() == '':  # если нажали только Enter (строка пустая)
            break


def display_grammemes(for_n_grams=True):
    """
    Отображает справочную информацию о грамматических категориях и их обозначениях.

    :param for_n_grams: Если True, отображает информацию о частеречных n-граммах.
                        Если False, отображает информацию о морфологических аннотациях.
    """
    if for_n_grams:
        print(
            Fore.LIGHTGREEN_EX + Style.BRIGHT + "\nДАЛЕЕ БУДЕТ ПОКАЗАН АНАЛИЗ ЧАСТЕРЕЧНЫХ N-ГРАММОВ С ИСПОЛЬЗОВАНИЕМ PYMORPHY" + Fore.RESET)
        print(
            Fore.LIGHTRED_EX + Style.BRIGHT + "\nВНИМАТЕЛЬНО ПОСМОТРИТЕ НА ОБОЗНАЧЕНИЯ ЧАСТЕЙ РЕЧИ ПЕРЕД ТЕМ, КАК ПРОДОЛЖИТЬ" + Fore.RESET)
    else:
        print(
            Fore.LIGHTRED_EX + Style.BRIGHT + "\nВНИМАТЕЛЬНО ПОСМОТРИТЕ НА ОБОЗНАЧЕНИЯ ЧАСТЕЙ РЕЧИ И ИХ КАТЕГОРИЙ ПЕРЕД ТЕМ, КАК ПРОДОЛЖИТЬ" + Fore.RESET)

    table = Table()
    table.add_column("POS", no_wrap=True, justify="center", style="bold")
    table.add_column("Значение")
    table.add_column("Примеры")
    if for_n_grams:
        for grammeme, (description, examples) in GRAMMEMES_NGRAMS.items():
            table.add_row(grammeme, description, examples)
    else:
        for grammeme, (description, examples) in GRAMMEMES_MORPH_ANNOTATION.items():
            table.add_row(grammeme, description, examples)

    console.print(table)


def format_morphological_features(tag):
    """
    Преобразует морфологические признаки в формат feature=value.

    :param tag: Морфологическая метка (тег) для преобразования.
    :return: Строка с форматированными морфологическими признаками.
    """
    features = []
    # Добавляем морфологические при
    if 'anim' in tag:
        features.append("Animacy=Animate")
    if 'inan' in tag:
        features.append("Animacy=Inanimate")
    if 'nomn' in tag:
        features.append("Case=Nominative")
    if 'gent' in tag:
        features.append("Case=Genetive")
    if 'datv' in tag:
        features.append("Case=Dative")
    if 'accs' in tag:
        features.append("Case=Accusative")
    if 'ablt' in tag:
        features.append("Case=Instrumental")
    if 'loct' in tag:
        features.append("Case=Locative")
    if 'sing' in tag:
        features.append("Number=Singular")
    if 'plur' in tag:
        features.append("Number=Plural")
    if 'masc' in tag:
        features.append("Gender=Masculine")
    if 'femn' in tag:
        features.append("Gender=Feminine")
    if 'neut' in tag:
        features.append("Gender=Neuter")

    if '1per' in tag:
        features.append("Person=1st")
    if '2per' in tag:
        features.append("Person=2nd")
    if '3per' in tag:
        features.append("Person=3d")

    # Признаки для глаголов
    if 'perf' in tag:
        features.append("Aspect=Perfect")
    if 'impf' in tag:
        features.append("Aspect=Imperfect")
    if 'pres' in tag:
        features.append("Tense=Present")
    if 'past' in tag:
        features.append("Tense=Past")
    if 'futr' in tag:
        features.append("Tense=Future")
    if 'tran' in tag:
        features.append("Transitivity=Transitive")
    if 'intr' in tag:
        features.append("Transitivity=Intransitive")
    if 'indc' in tag:
        features.append("Mood=Indicative")
    if 'impr' in tag:
        features.append("Mood=Imperative")
    if 'actv' in tag:
        features.append("Voice=Active")
    if 'pssv' in tag:
        features.append("Voice=Passive")

    return ', '.join(features)


def display_morphological_annotation(sentences_info):
    """
    Отображает морфологическую разметку текста в виде таблиц по предложениям.

    :param sentences_info: Список словарей, содержащих информацию о лексемах, их леммах,
     частях речи и морфологических характеристиках.
    """
    print("\n" + Fore.LIGHTWHITE_EX + "*" * 100)
    print(
        Fore.GREEN + Style.BRIGHT + "                                   МОРФОЛОГИЧЕСКАЯ РАЗМЕТКА" + Fore.RESET)
    print("" + Fore.LIGHTWHITE_EX + "*" * 100)

    def show_annot_info():
        display_grammemes(False)
        wait_for_enter_to_analyze()
        display_gr_categories()

    while True:
        user_input = input(
            Fore.LIGHTGREEN_EX + Style.BRIGHT + "Отобразить справку об используемых обозначениях (y/n)?\n" + Fore.RESET).strip().lower()
        if user_input.lower() == "y":
            show_annot_info()
            break
        elif user_input.lower() == "n":
            break
        else:
            print(
                Fore.LIGHTRED_EX + "\nНеверный ввод. Пожалуйста, выберите один из возможных вариантов (y/n)." + Fore.RESET)
            continue

    if sentences_info:
        total_sentences = len(sentences_info)
        start_index = 0
        print(
            Fore.LIGHTGREEN_EX + Style.BRIGHT + "\nДалее на экран будет выводиться по 5 предложений текста." + Fore.RESET)
        wait_for_enter_to_analyze()

        while start_index < total_sentences:
            end_index = min(start_index + 5, total_sentences)
            for index in range(start_index, end_index):
                sentence_info = sentences_info[index]
                # Создаем таблицу для каждого предложения
                table = PrettyTable()
                table.field_names = [Fore.BLUE + Style.BRIGHT + "Словоформа", "Лемма", "Часть речи",
                                     "Морфологические характеристики" + Fore.RESET]
                for info in sentence_info.values():
                    table.add_row([info["token"], info["lemma"], info["POS"], info["morph_features"]])

                print("\n" + Fore.LIGHTBLUE_EX + Style.BRIGHT + "*" * 150)
                print(Fore.GREEN + Style.BRIGHT + f"Предложение {index + 1}:")
                print(table)

            start_index = end_index
            print(
                Fore.LIGHTWHITE_EX + Style.BRIGHT + f"Отображено {start_index} предложений. Всего предложений: {total_sentences} " + Fore.RESET)
            if start_index < total_sentences:
                while True:
                    user_input = input(
                        Fore.GREEN + Style.BRIGHT + "Отобразить следующие 5 предложений? (y/n)" + Fore.RESET).strip().lower()
                    if user_input in ["y", "n"]:
                        break
                    print(
                        Fore.LIGHTRED_EX + "\nНеверный ввод. Пожалуйста, выберите один из возможных вариантов (y/n)." + Fore.RESET)

                if user_input == "n":
                    break

    else:
        print("Морфологический анализ еще не был выполнен.")


def display_gr_categories():
    """
    Отображает таблицу с видами грамматических категорий и их подкатегориями.
    """
    console = Console()

    for category, subcategories in GRAMMEMES_MORPH_ANNOTATION_GRAM_CATEGORIES.items():
        print(
            Fore.GREEN + Style.BRIGHT + f"* {category.upper()}" + Fore.RESET)

        table = Table()
        table.add_column("Подкатегория", width=20, justify="center")
        table.add_column("Описание", justify="center")

        for subcategory, description in subcategories.items():
            table.add_row(subcategory, description)

        console.print(table)
        wait_for_enter_to_analyze()


def display_position_explanation():
    """
     Отображает объяснение позиций токенов в предложениях.
     """
    print(Fore.LIGHTGREEN_EX + Style.BRIGHT + "Анализируются следующие позиции в предложениях:" + Fore.RESET)
    print(Fore.LIGHTWHITE_EX + Style.BRIGHT + " - first - Первый токен" + Fore.RESET)
    print(Fore.LIGHTWHITE_EX + Style.BRIGHT + " - second - Второй токен" + Fore.RESET)
    print(Fore.LIGHTWHITE_EX + Style.BRIGHT + " - antepenultimate - Третий токен с конца" + Fore.RESET)
    print(Fore.LIGHTWHITE_EX + Style.BRIGHT + " - penultimate - Предпоследний токен" + Fore.RESET)
    print(Fore.LIGHTWHITE_EX + Style.BRIGHT + " - last - Последний токен" + Fore.RESET)
    wait_for_enter_to_analyze()


def get_syntactic_annotation(text):
    """Метод для выполнения синтаксической разметки текста с использованием Natasha."""
    doc = Doc(text)
    segmenter = Segmenter()
    emb = NewsEmbedding()
    morph_tagger = NewsMorphTagger(emb)
    syntax_parser = NewsSyntaxParser(emb)
    # Сегментация на предложения для дальнейшего анализа
    doc.segment(segmenter)
    # Морфологический анализ для дальнейшего синтаксического анализа
    doc.tag_morph(morph_tagger)
    # Анализ синтаксиса
    doc.parse_syntax(syntax_parser)
    # Собираем синтаксическую разметку в строку
    tokens_info = []
    i = 0

    for token in doc.tokens:
        # Получаем информацию о каждом токене
        token_info = {
            f"TOKEN {i + 1}": token.text,
            "id": token.id,
            "head_id": token.head_id,
            "pos": token.pos,
            "dependency": token.rel,
            "features": token.feats
        }
        tokens_info.append(token_info)
        i += 1

    return doc


def display_syntactic_annotation(doc):
    """Метод для отображения синтаксической разметки в виде древовидной структуры, аналогичной Natasha."""
    print("\n" + Fore.LIGHTWHITE_EX + "*" * 100)
    print(
        Fore.GREEN + Style.BRIGHT + "                                   СИНТАКСИЧЕСКАЯ РАЗМЕТКА" + Fore.RESET)
    print("" + Fore.LIGHTWHITE_EX + "*" * 100)
    print(Fore.LIGHTGREEN_EX + Style.BRIGHT +
          "В  программе используется разметка синтаксических зависимостей в формате (UD) Universal "
          "Dependencies.\n"
          "Cинтаксический анализ будет представлен в виде древовидной структуры. На на экран будет выводиться по"
          "\n5 предложений текста.\n" + Fore.RESET)
    wait_for_enter_to_analyze()
    total_sentences = len(doc.sents)
    start = 0
    batch_size = 5

    while start < total_sentences:
        end = min(start + batch_size, total_sentences)

        for i in range(start, end):
            print(Fore.GREEN + Style.BRIGHT + f'\nПРЕДЛОЖЕНИЕ {i + 1}:\n' + Fore.RESET)
            doc.sents[i].syntax.print()
            print("\n" + Fore.LIGHTBLUE_EX + Style.BRIGHT + "*" * 150)

        start = end  # Обновляем значение start до фактического конца отображенных предложений
        print(
            Fore.LIGHTGREEN_EX + Style.BRIGHT + f"Отображено {start} предложений. Всего предложений:"
                                                f" {total_sentences}" + Fore.RESET)

        if start < total_sentences:
            user_input = input(
                Fore.GREEN + Style.BRIGHT + "Отобразить следующие 5 предложений (y/n)?"
                                                     " \n" + Fore.RESET).strip().lower()

            while user_input not in ['y', 'n']:
                user_input = input(
                    Fore.LIGHTRED_EX + "Неверный ввод. Пожалуйста, выберите один из возможных вариантов (y/n):"
                                       " \n" + Fore.RESET).strip().lower()

            if user_input == 'n':
                break


def check_db_exists(db_name):
    """
    Проверяет, существует ли база данных SQLite с заданным именем.

    :param db_name Имя базы данных (путь к файлу базы данных).
    :return True, если база данных существует, иначе False.
    """
    return os.path.exists(db_name)


def choose_universal():
    while True:
        print(Fore.GREEN + Style.BRIGHT + "\n Выберите опцию: ")
        print(Fore.GREEN  + Style.BRIGHT
              + "  1."
              + Style.NORMAL + Fore.BLACK + " Средние показатели индикаторов характеристики Simplification")
        print(Fore.GREEN + Style.BRIGHT
              + "  2."
              + Style.NORMAL + Fore.BLACK + " Средние показатели индикаторов характеристики Normalisation")
        print(Fore.GREEN + Style.BRIGHT
              + "  3."
              + Style.NORMAL + Fore.BLACK + " Средние показатели индикаторов характеристики Explicitation")
        print(Fore.GREEN + Style.BRIGHT
              + "  4."
              + Style.NORMAL + Fore.BLACK + " Средние показатели индикаторов характеристики Interference")
        print(Fore.GREEN + Style.BRIGHT
              + "  5."
              + Style.NORMAL + Fore.BLACK + " Средние показатели остальных индикаторов")
        print(Fore.BLACK + Style.BRIGHT
              + "  6."
              + Style.NORMAL + Fore.LIGHTBLACK_EX + " Выйти в главное меню")

        choice = input(
            Fore.GREEN + Style.BRIGHT + "Введите номер опции.\n " + Fore.RESET)
        try:
            choice = int(choice)
            if 1 <= choice <= 6:
                return str(choice)  # Возвращаем строку с номером выбранной опции
            else:
                print(Fore.RED + Style.BRIGHT + "Неверный выбор. Пожалуйста, попробуйте снова.")

        except ValueError:
            print(
                Fore.RED + Style.BRIGHT + "Пожалуйста, введите числовое снова.")
            continue

    return choice


def choose_db():
    while True:
        print(Fore.GREEN + Style.BRIGHT + "\nВыберите базу данных, в которую хотите"
                                          " сохранить результат анализа текста:")
        print(Fore.GREEN + Style.BRIGHT + "1."
              + Style.NORMAL + Fore.BLACK + " База непереводных текстов")
        print(Fore.GREEN + Style.BRIGHT
              + "2." + Style.NORMAL + Fore.BLACK + " База машинных переводов")
        print(Fore.GREEN + Style.BRIGHT
              + "3." + Style.NORMAL + Fore.BLACK + " База ручных переводов")
        print(Fore.LIGHTBLACK_EX + Style.BRIGHT
              + "4." + Style.NORMAL + Fore.LIGHTBLACK_EX + " Вернуться в главное меню")
        db_choice = input(Fore.GREEN + Style.BRIGHT + "Выберите номер базы данных:\n")
        if db_choice == "1":
            db = NON_TRANSLATED_DB_NAME
            break
        elif db_choice == "2":
            db = MACHINE_TRANSLATED_DB_NAME
            break
        elif db_choice == "3":
            db = HUMAN_TRANSLATED_DB_NAME
            break
        elif db_choice == "4":
            return
        else:
            print(Fore.LIGHTRED_EX + Style.BRIGHT + "Неверный выбор базы данных. Пожалуйста, попробуйте снова.")
    return db
