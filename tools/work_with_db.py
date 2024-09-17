# -*- coding: utf-8 -*-
import json
from collections import defaultdict

import re
import sqlite3 as sq

from colorama import Fore, Style, init
from rich.table import Table
from rich.console import Console

from tools.interference.contextual_func_words import print_trigram_tables_with_func_w
from tools.miscellaneous.flesh_readability_index import display_readability_index
from tools.miscellaneous.func_words_freqs import print_func_w__frequencies
from tools.interference.n_grams_analyzer import display_ngrams_summary
from tools.explicitation.named_entities_extraction import display_entities
from tools.miscellaneous.passive_to_all_verbs_ratio import print_passive_verbs_ratio
from tools.normalisation.pmi import calculate_pmi, display_pmi_table
from tools.interference.positional_token_freq import print_frequencies
from tools.interference.positional_tokens_contexts_by_sent import print_positions
from tools.miscellaneous.pronouns_freq import print_pronoun_frequencies
from tools.miscellaneous.punct_analysis import display_punctuation_analysis
from tools.normalisation.repetition import print_word_occurrences_table
from tools.explicitation.sci_dm_analysis import print_dm_analysis_results
from tools.core.utils import wait_for_enter_to_analyze, wait_for_enter_to_choose_opt, display_morphological_annotation, \
    display_grammemes, display_position_explanation

console = Console()
init(autoreset=True)


class SaveToDatabase:
    def __init__(self, db_name):
        self.db_name = db_name
        self.connection = None
        self.cursor = None
        self.connect_db()
        self.create_tables()

    def connect_db(self):
        """Подключение к базе данных SQLite или создание новой базы данных."""
        self.connection = sq.connect(self.db_name)
        self.cursor = self.connection.cursor()

    def __enter__(self):
        # Открываем соединение с базой данных и возвращаем объект для использования в блоке with
        self.connect_db()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        # Закрываем соединение с базой данных
        if self.connection:
            self.connection.commit()
            self.connection.close()
        self.connection = None
        self.cursor = None

    def display_corpus_info(self):
        """Отображает информацию о корпусе текстов"""
        # Извлечение количества текстов
        corpus_name = ''
        if self.db_name == 'auth_texts_corpus.db':
            corpus_name = 'КОРПУС АУТЕНТИЧНЫХ ТЕКСТОВ'
        elif self.db_name == 'mt_texts_corpus.db':
            corpus_name = 'КОРПУС МАШИННЫХ ПЕРЕВОДОВ'
        elif self.db_name == 'ht_texts_corpus.db':
            corpus_name = 'КОРПУС ПЕРЕВОДОВ, СДЕЛАННЫХ ЧЕЛОВЕКОМ'

        self.cursor.execute("SELECT COUNT(*) FROM Text_Passport")
        num_texts = self.cursor.fetchone()[0]
        if num_texts > 0:
            print("\n" + Fore.LIGHTWHITE_EX + "*" * 100)
            print(
                Fore.LIGHTYELLOW_EX + Style.BRIGHT + "                      ВЫБРАН" + Fore.LIGHTRED_EX + Style.BRIGHT + f" {corpus_name}" + Fore.RESET)
            print(Fore.LIGHTWHITE_EX + "*" * 100)
            print(
                Fore.LIGHTYELLOW_EX + Style.BRIGHT + "\nВСЕГО ТЕКСТОВ В ВЫБРАННОМ КОРПУСЕ:" + Fore.LIGHTRED_EX + Style.BRIGHT + f" {num_texts}" + Fore.RESET)

            while True:
                print(Fore.LIGHTYELLOW_EX + Style.BRIGHT + "\n Выберите опцию: ")
                print(Fore.LIGHTWHITE_EX + "  1. Средние показатели индикаторов универсалии Simplification")
                print(Fore.LIGHTWHITE_EX + "  2. Средние показатели индикаторов универсалии Normalisation")
                print(Fore.LIGHTWHITE_EX + "  3. Средние показатели индикаторов универсалии Explicitation")
                print(Fore.LIGHTWHITE_EX + "  4. Средние показатели индикаторов универсалии Interference")
                print(Fore.LIGHTWHITE_EX + "  5. Средние показатели остальных индикаторов")
                print(Fore.WHITE + "  6. Выйти в главное меню")

                choice = input(
                    Fore.LIGHTYELLOW_EX + Style.BRIGHT + "Введите номер опции.\n " + Fore.RESET)

                if choice == "1":
                    self.display_simplification_features_for_corpus()

                elif choice == "2":
                    self.display_normalisation_features_for_corpus()

                    def show_pmi():
                        print("\n" + Fore.LIGHTWHITE_EX + "*" * 100)
                        print(
                            Fore.LIGHTYELLOW_EX + Style.BRIGHT + "                        АНАЛИЗ " + Fore.LIGHTRED_EX + Style.BRIGHT + "ПОКАЗАТЕЛЯ PMI" + Fore.LIGHTYELLOW_EX + Style.BRIGHT + " ДЛЯ КОРПУСА ТЕКСТОВ" + Fore.RESET)
                        print(Fore.LIGHTWHITE_EX + "*" * 100)

                        print(
                            Fore.LIGHTYELLOW_EX + Style.BRIGHT + "\nДалее будет проведен подсчет PMI всех рядом"
                                                                 "стоящих друг с другом (word1word2) биграммов в "
                                                                 "тексте.")
                        print(
                            Fore.LIGHTRED_EX + Style.BRIGHT + "ВНИМАНИЕ! Точность подсчета PMI напрямую зависит от "
                                                              "размера корпуса.При небольшом размере корпуса\n"
                                                              "высока вероятность получить искусственно завышенные "
                                                              "значения PMI. Случайные редкие словосочетания\n"
                                                              "могут выявить высокие значения PMI, что будет говорить "
                                                              "не о сильной ассоциативной связи между\n"
                                                              "словами, а о недостаточно большом размере корпуса.\n")
                        print(
                            Fore.LIGHTGREEN_EX + Style.BRIGHT + "При большом размере корпуса подсчет PMI может занять какое-то время. "
                                                        "Пожалуйста, будьте готовы подождать.\n")

                        wait_for_enter_to_analyze()
                        # Собираем тексты для подсчета PMI
                        self.cursor.execute("SELECT text FROM Text_Passport")
                        texts = self.cursor.fetchall()
                        corpus_set = set(text[0] for text in texts)

                        pmi_values, total_above_zero = calculate_pmi(corpus_set=corpus_set)

                        # Таблица для отображения результатов PMI
                        print(
                            Fore.LIGHTYELLOW_EX + Style.BRIGHT + f"\nPMI БИГРАММОВ КОРПУСА" + Fore.RESET)
                        print(
                            Fore.LIGHTWHITE_EX + Style.BRIGHT + f'Всего найдено {total_above_zero} биграммов с PMI > 0.')

                        while True:
                            print(
                                Fore.LIGHTYELLOW_EX + Style.BRIGHT + "Отобразить биграммы и их PMI(y/n)?")
                            show_bigrams_pmi = input()
                            if show_bigrams_pmi.lower() == 'y':
                                print(
                                    Fore.LIGHTRED_EX + Style.BRIGHT + "\nВнимание! Вывод значений PMI для всех биграммов может занять"
                                                              " много места на экране. \nБиграммы будут представлены в лемматизированном виде.")
                                display_pmi_table(pmi_values)
                                wait_for_enter_to_choose_opt()
                                break
                            elif show_bigrams_pmi.lower() == 'n':
                                break
                            else:
                                print(Fore.LIGHTRED_EX + Style.BRIGHT + "Неверный выбор. Пожалуйста, попробуйте снова.")
                                continue

                    while True:
                        print(
                            Fore.LIGHTYELLOW_EX + Style.BRIGHT + "\nОтобразить PMI (Pointwise Mutual Information) корпуса текстов (y/n)?")
                        show_pmi_choice = input()
                        if show_pmi_choice.lower() == 'y':
                            show_pmi()
                            break
                        elif show_pmi_choice.lower() == 'n':
                            break
                        else:
                            print(Fore.LIGHTRED_EX + Style.BRIGHT + "Неверный выбор. Пожалуйста, попробуйте снова.")
                            continue

                elif choice == "3":
                    self.display_explicitation_features_for_corpus()

                elif choice == "4":
                    self.display_interference_features_for_corpus()

                elif choice == "5":
                    self.display_miscellaneous_features_for_corpus()

                elif choice == "6":
                    print(Fore.LIGHTYELLOW_EX + "Выход из программы." + Fore.RESET)
                    break
                else:
                    print(
                        Fore.LIGHTRED_EX + "Неправильный выбор. Пожалуйста, выберите один из предложенных вариантов.\n" + Fore.RESET)
                    continue

        else:
            if self.db_name == 'ht_texts_corpus.db':
                print(
                    Fore.LIGHTRED_EX + Style.BRIGHT + f"\n{corpus_name}" + Fore.LIGHTYELLOW_EX + Style.BRIGHT + ", НЕ СОДЕРЖИТ НИ ОДНОГО ТЕКСТА" + Fore.RESET)
                wait_for_enter_to_choose_opt()
            else:
                print(
                    Fore.LIGHTRED_EX + Style.BRIGHT + f"\n{corpus_name}" + Fore.LIGHTYELLOW_EX + Style.BRIGHT + " НЕ СОДЕРЖИТ НИ ОДНОГО ТЕКСТА" + Fore.RESET)
                wait_for_enter_to_choose_opt()

    def display_texts(self):
        """Отображает все тексты с их порядковыми номерами и
         позволяет выбрать один для отображения подробной информации."""
        # Извлекаем все тексты
        texts = self.fetch_text_passport()

        while True:
            # Запрашиваем у пользователя выбор текста
            print(Fore.LIGHTYELLOW_EX + Style.BRIGHT + "\nСПИСОК ДОСТУПНЫХ ТЕКСТОВ:" + Fore.RESET)
            print(Fore.WHITE + f"0. Выйти в главное меню")
            for idx, text in enumerate(texts, 1):
                text_id, title = text[0], text[2]
                print(f"{idx}. {title.capitalize()}")
            try:
                choice = int(input(Fore.LIGHTYELLOW_EX + Style.BRIGHT + "Введите номер текста для отображения "
                                                                        "информации: \n" + Fore.RESET)) - 1
                if choice == -1:  # поскольку мы вычитаем 1, 0 становится -1
                    break

                elif 0 <= choice < len(texts):
                    selected_text = texts[choice]
                    selected_text_id = selected_text[0]
                    self.display_text_info(selected_text_id)
                    break
                else:
                    print(
                        Fore.LIGHTRED_EX + Style.BRIGHT + "Ошибка: Выбран неверный номер текста. Пожалуйста, попробуйте снова." + Fore.RESET)
            except ValueError:
                print(Fore.LIGHTRED_EX + Style.BRIGHT + "Пожалуйста, введите числовое значение.\n" + Fore.RESET)

    def display_text_info(self, text_id):
        """Отображает информацию о конкретном тексте по его ID."""
        text_info = self.fetch_text_passport(text_id)

        if text_info:
            text_info = text_info[0]
            print(
                Fore.LIGHTYELLOW_EX + Style.BRIGHT + f"\n                 ПАСПОРТ ТЕКСТА {text_info[0]} " + Fore.RESET)

            table = Table()

            table.add_column("Поле", no_wrap=True, style="bold", )
            table.add_column("Значение", justify="center", min_width=20)

            table.add_row("Название", text_info[2])
            table.add_row("Предметная область", text_info[3])
            table.add_row("Ключевые слова", text_info[4])
            table.add_row("Год публикации", str(text_info[5]))
            table.add_row("Место публикации (журнал)", text_info[6])
            table.add_row("Автор(ы)", text_info[7])
            table.add_row("Пол автора(ов)", text_info[8])
            table.add_row("Год рождения автора(ов)", text_info[9])
            console.print(table)
            wait_for_enter_to_analyze()

            exit_loop = False
            while True:
                print(Fore.LIGHTYELLOW_EX + Style.BRIGHT + "Выберите опцию: ")
                print(Fore.LIGHTWHITE_EX + " 1. Текст статьи")
                print(Fore.LIGHTWHITE_EX + " 2. Морфологическая разметка")
                print(Fore.LIGHTWHITE_EX + " 3. Синтаксическая разметка")
                print(Fore.LIGHTWHITE_EX + " 4. Анализ индикаторов универсалии Simplification")
                print(Fore.LIGHTWHITE_EX + " 5. Анализ индикаторов универсалии Normalisation")
                print(Fore.LIGHTWHITE_EX + " 6. Анализ индикаторов универсалии Explicitation")
                print(Fore.LIGHTWHITE_EX + " 7. Анализ индикаторов универсалии Interference")
                print(Fore.LIGHTWHITE_EX + " 8. Анализ остальных индикаторов")
                print(Fore.LIGHTWHITE_EX + " 9. Удалить запись о данном тексте из БД")
                print(Fore.WHITE + " 10. Выйти в главное меню")

                choice = input(
                    Fore.LIGHTYELLOW_EX + Style.BRIGHT + "Выберите, какую информацию о тексте"
                                                         " хотите посмотреть.\n " + Fore.RESET)

                if choice == "1":
                    print(
                        Fore.LIGHTYELLOW_EX + Style.BRIGHT + "ТЕКСТ: " + Fore.LIGHTWHITE_EX +
                        Style.BRIGHT + f"\n{text_info[1]}")
                    wait_for_enter_to_choose_opt()
                elif choice == "2":
                    self.display_morphological_annotation(text_id)
                    wait_for_enter_to_choose_opt()
                elif choice == "3":
                    from start_analysis import CorpusText
                    corpus = CorpusText(db=self.db_name, text=text_info[1])
                    corpus.get_syntactic_annotation(False)
                    corpus.display_syntactic_annotation()
                    wait_for_enter_to_choose_opt()
                elif choice == "4":
                    self.display_simplification_analysis(text_id)
                    wait_for_enter_to_choose_opt()
                elif choice == "5":
                    self.display_normalisation_analysis(text_id)
                    wait_for_enter_to_choose_opt()
                elif choice == "6":
                    self.display_explicitation_analysis(text_id)
                    wait_for_enter_to_choose_opt()
                elif choice == "7":
                    self.display_interference_analysis(text_id)
                    wait_for_enter_to_choose_opt()
                elif choice == "8":
                    self.display_miscellaneous_features_analysis(text_id)
                    wait_for_enter_to_choose_opt()
                elif choice == "9":
                    while True:
                        confirm = input(
                            Fore.LIGHTRED_EX + Style.BRIGHT + "Вы уверены, что хотите удалить запись об этом тексте (y/n)?\nЭто действие будет не отменить.\n" + Fore.RESET).lower()
                        if confirm == 'y':
                            self.delete_text_from_corpus(text_id)
                            exit_loop = True
                            break
                        elif confirm == 'n':
                            print(Fore.LIGHTYELLOW_EX + "Удаление отменено." + Fore.RESET)
                            break
                        else:
                            print(
                                Fore.LIGHTRED_EX + Style.BRIGHT + "\nПожалуйста, введите 'y' для удаления или 'n' для отмены." + Fore.RESET)

                elif choice == "10":
                    print("Выход из программы.")
                    break

                if exit_loop:
                    break

        else:
            print("Текст с таким ID не найден.")

    def create_tables(self):
        """Создание таблиц для хранения результатов анализа текста."""
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS Text_Passport (
        text_id INTEGER PRIMARY KEY AUTOINCREMENT,
        text TEXT NOT NULL,
        title TEXT NOT NULL,
        subject_area TEXT,
        keywords TEXT,
        publication_year INTEGER NOT NULL,
        published_in TEXT,
        authors TEXT,
        author_gender TEXT,
        author_birth_year TEXT
        )""")

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS Simplification_features(
        text_id INTEGER PRIMARY KEY AUTOINCREMENT,
        
        lexical_density REAL NOT NULL,
        
        ttr_lex_variety REAL NOT NULL,
        log_ttr_lex_variety REAL NOT NULL,
        modified_lex_variety REAL NOT NULL,
        
        mean_word_length REAL NOT NULL,
        
        syllable_ratio REAL NOT NULL,
        total_syllables_count INTEGER NOT NULL,
        
        tokens_mean_sent_length REAL NOT NULL,
        chars_mean_sent_length REAL NOT NULL,
        
        mean_word_rank_1 REAL NOT NULL,
        mean_word_rank_2 REAL NOT NULL,
        
        
        most_freq_words TEXT NOT NULL
        )""")

        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS Normalisation_features(
        text_id INTEGER PRIMARY KEY AUTOINCREMENT,
        repetition REAL NOT NULL,
        repeated_content_words_count TEXT NOT NULL,
        repeated_content_words INTEGER NOT NULL,
        total_word_tokens INTEGER NOT NULL
        )''')

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS Explicitation_features (
        text_id INTEGER PRIMARY KEY AUTOINCREMENT,
        explicit_naming_ratio REAL,
        single_naming REAL,
        
        mean_multiple_naming REAL,
        single_entities TEXT,
        single_entities_count INTEGER,
        multiple_entities TEXT,
        multiple_entities_count INTEGER,
        
        
        named_entities TEXT,
        named_entities_count INTEGER,
        
        sci_markers_total_count INTEGER,
        found_sci_dms TEXT,
        markers_counts TEXT,
        
        topic_intro_dm_count INTEGER,
        topic_intro_dm_in_ord TEXT,
        topic_intro_dm_freq  REAL,
        
        info_sequence_count INTEGER,
        info_sequence_in_ord TEXT,
        info_sequence_freq REAL,
        
        illustration_dm_count INTEGER,
        illustration_dm_in_ord TEXT,
        illustration_dm_freq REAL,
        
        material_sequence_count INTEGER,
        material_sequence_in_ord TEXT,
        material_sequence_freq REAL,
        
        
        conclusion_dm_count INTEGER,
        conclusion_dm_in_ord TEXT,
        conclusion_dm_freq REAL,
        
        
        intro_new_addit_info_count INTEGER,
        intro_new_addit_info_in_ord TEXT,
        intro_new_addit_info_freq REAL,
        
        
        info_explanation_or_repetition_count INTEGER,
        info_explanation_or_repetition_in_ord TEXT,
        info_explanation_or_repetition_freq REAL,
        
        
        contrast_dm_count INTEGER,
        contrast_dm_in_ord TEXT,
        contrast_dm_freq REAL,
        
        examples_introduction_dm_count INTEGER,
        examples_introduction_dm_in_ord TEXT,
        examples_introduction_dm_freq REAL,
        
        author_opinion_count INTEGER,
        author_opinion_in_ord TEXT,
        author_opinion_freq REAL,
        
        categorical_attitude_dm_count INTEGER,
        categorical_attitude_dm_in_ord TEXT,
        categorical_attitude_dm_freq REAL,
        
        less_categorical_attitude_dm_count INTEGER,
        less_categorical_attitude_dm_in_ord TEXT,
        less_categorical_attitude_dm_freq REAL,
        
        call_to_action_dm_count INTEGER,
        call_to_action_dm_in_ord TEXT,
        call_to_action_dm_freq REAL,
        
        joint_action_count INTEGER,
        joint_action_in_ord TEXT,
        joint_action_freq REAL,
        
        putting_emphasis_dm_count INTEGER,
        putting_emphasis_dm_in_ord TEXT,
        putting_emphasis_dm_freq REAL,
        
        refer_to_background_knowledge_count INTEGER,
        refer_to_background_knowledge_in_ord TEXT,
        refer_to_background_knowledge_freq REAL
        ) """)

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS Interference_features(
        text_id INTEGER PRIMARY KEY AUTOINCREMENT,
        pos_unigrams_counts TEXT NOT NULL,
        pos_unigrams_freq TEXT NOT NULL,
        pos_bigrams_counts  TEXT NOT NULL,
        pos_bigrams_freq  TEXT NOT NULL,
        pos_trigrams_counts  TEXT NOT NULL,
        pos_trigrams_freq  TEXT NOT NULL,
        
        char_unigram_counts TEXT NOT NULL,
        char_unigram_freq TEXT NOT NULL,
        char_bigram_counts TEXT NOT NULL,
        char_bigram_freq TEXT NOT NULL,
        char_trigram_counts TEXT NOT NULL,
        char_trigram_freq TEXT NOT NULL,
        
        token_positions_normalized_frequencies TEXT NOT NULL,
        token_positions_counts  TEXT NOT NULL,
        token_positions_in_sent TEXT NOT NULL,
        
        func_w_trigrams_freqs TEXT NOT NULL,
        func_w_trigram_with_pos_counts TEXT NOT NULL,
        func_w_full_contexts TEXT NOT NULL
               )""")

        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS Miscellaneous_features(
        text_id INTEGER PRIMARY KEY AUTOINCREMENT,
        func_words_freq TEXT NOT NULL,
        func_words_counts TEXT NOT NULL,
        
        pronoun_frequencies TEXT NOT NULL,
        pronoun_counts TEXT NOT NULL,
        
        punct_marks_normalized_frequency TEXT NOT NULL,
        punct_marks_to_all_punct_frequency TEXT NOT NULL,
        punctuation_counts TEXT NOT NULL,
        
        passive_to_all_v_ratio REAL NOT NULL,
        passive_verbs TEXT NOT NULL,
        passive_verbs_count INTEGER NOT NULL,
        all_verbs TEXT NOT NULL,
        all_verbs_count INTEGER NOT NULL,
        
        readability_index REAL NOT NULL
        )''')

        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS Morphological_annotation (
        text_id INTEGER PRIMARY KEY AUTOINCREMENT,
        morph_annotation TEXT NOT NULL
        )''')

        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS Syntactic_annotation (
        text_id INTEGER PRIMARY KEY AUTOINCREMENT,
        syntactic_annotation TEXT NOT NULL
        )''')

        self.connection.commit()

    def insert_morphological_annotation(self, morph_annotation):
        """Сохраняет морфологическую разметку в базу данных."""
        self.cursor.execute("""
            INSERT INTO Morphological_annotation (morph_annotation)
            VALUES (?)
        """, (morph_annotation,))
        self.connection.commit()

    def insert_syntactic_annotation(self, syntactic_annotation):
        """Сохраняет синтаксическую разметку в базу данных."""
        self.cursor.execute("""
            INSERT INTO Syntactic_annotation (syntactic_annotation)
            VALUES (?)
        """, (syntactic_annotation,))
        self.connection.commit()

    def insert_simplification_features(self, lexical_density, ttr_lex_variety,
                                       log_ttr_lex_variety, modified_lex_variety, mean_word_length,
                                       syllable_ratio, total_syllables_count, tokens_mean_sent_length,
                                       chars_mean_sent_length, mean_word_rank_1, mean_word_rank_2, most_freq_words):
        """Вставка данных в таблицу Simplification_features"""
        self.cursor.execute('''
        INSERT INTO Simplification_features (lexical_density, ttr_lex_variety,
                                             log_ttr_lex_variety, modified_lex_variety, mean_word_length, 
                                             syllable_ratio, total_syllables_count, tokens_mean_sent_length, 
                                             chars_mean_sent_length,  mean_word_rank_1, mean_word_rank_2, most_freq_words)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?, ?)
        ''', (lexical_density, ttr_lex_variety, log_ttr_lex_variety,
              modified_lex_variety, mean_word_length, syllable_ratio, total_syllables_count,
              tokens_mean_sent_length, chars_mean_sent_length, mean_word_rank_1, mean_word_rank_2, most_freq_words))
        self.connection.commit()

    def insert_normalisation_features(self, repetition, repeated_content_words_count, repeated_content_words,
                                      total_word_tokens):
        """Вставка данных в таблицу Normalisation_features"""
        self.cursor.execute('''
        INSERT INTO Normalisation_features (repetition, repeated_content_words_count, 
        repeated_content_words, total_word_tokens)
        VALUES (?, ?, ?, ?)
        ''', (repetition, repeated_content_words_count, repeated_content_words, total_word_tokens))
        self.connection.commit()

    def insert_explicitation_features(self, explicit_naming_ratio, single_naming, mean_multiple_naming, single_entities,
                                      single_entities_count, multiple_entities, multiple_entities_count, named_entities,
                                      named_entities_count,
                                      sci_markers_total_count, found_sci_dms, markers_counts,
                                      topic_intro_dm_count, topic_intro_dm_in_ord, topic_intro_dm_freq,
                                      info_sequence_count, info_sequence_in_ord, info_sequence_freq,
                                      illustration_dm_count, illustration_dm_in_ord, illustration_dm_freq,
                                      material_sequence_count, material_sequence_in_ord, material_sequence_freq,
                                      conclusion_dm_count, conclusion_dm_in_ord, conclusion_dm_freq,
                                      intro_new_addit_info_count, intro_new_addit_info_in_ord,
                                      intro_new_addit_info_freq,
                                      info_explanation_or_repetition_count, info_explanation_or_repetition_in_ord,
                                      info_explanation_or_repetition_freq,
                                      contrast_dm_count, contrast_dm_in_ord, contrast_dm_freq,
                                      examples_introduction_dm_count, examples_introduction_dm_in_ord,
                                      examples_introduction_dm_freq,
                                      author_opinion_count, author_opinion_in_ord, author_opinion_freq,
                                      categorical_attitude_dm_count, categorical_attitude_dm_in_ord,
                                      categorical_attitude_dm_freq,
                                      less_categorical_attitude_dm_count, less_categorical_attitude_dm_in_ord,
                                      less_categorical_attitude_dm_freq,
                                      call_to_action_dm_count, call_to_action_dm_in_ord, call_to_action_dm_freq,
                                      joint_action_count, joint_action_in_ord, joint_action_freq,
                                      putting_emphasis_dm_count, putting_emphasis_dm_in_ord, putting_emphasis_dm_freq,
                                      refer_to_background_knowledge_count, refer_to_background_knowledge_in_ord,
                                      refer_to_background_knowledge_freq):
        """Вставка данных в таблицу Explicitation_features"""
        self.cursor.execute('''
        INSERT INTO Explicitation_features (explicit_naming_ratio, single_naming, mean_multiple_naming, single_entities,
                                      single_entities_count, multiple_entities, multiple_entities_count, named_entities,
                                      named_entities_count,
                                      sci_markers_total_count, found_sci_dms, markers_counts,
                                      topic_intro_dm_count, topic_intro_dm_in_ord, topic_intro_dm_freq,
                                      info_sequence_count, info_sequence_in_ord, info_sequence_freq,
                                      illustration_dm_count, illustration_dm_in_ord, illustration_dm_freq,
                                      material_sequence_count, material_sequence_in_ord, material_sequence_freq,
                                      conclusion_dm_count, conclusion_dm_in_ord, conclusion_dm_freq,
                                      intro_new_addit_info_count, intro_new_addit_info_in_ord, intro_new_addit_info_freq,
                                      info_explanation_or_repetition_count, info_explanation_or_repetition_in_ord,
                                      info_explanation_or_repetition_freq,
                                      contrast_dm_count, contrast_dm_in_ord, contrast_dm_freq,
                                      examples_introduction_dm_count, examples_introduction_dm_in_ord,
                                      examples_introduction_dm_freq,
                                      author_opinion_count, author_opinion_in_ord, author_opinion_freq,
                                      categorical_attitude_dm_count, categorical_attitude_dm_in_ord, categorical_attitude_dm_freq,
                                      less_categorical_attitude_dm_count, less_categorical_attitude_dm_in_ord, 
                                      less_categorical_attitude_dm_freq,
                                      call_to_action_dm_count, call_to_action_dm_in_ord, call_to_action_dm_freq,
                                      joint_action_count, joint_action_in_ord, joint_action_freq,
                                      putting_emphasis_dm_count, putting_emphasis_dm_in_ord, putting_emphasis_dm_freq,
                                      refer_to_background_knowledge_count, refer_to_background_knowledge_in_ord, 
                                      refer_to_background_knowledge_freq
                                      
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (explicit_naming_ratio, single_naming, mean_multiple_naming, single_entities,
              single_entities_count, multiple_entities, multiple_entities_count, named_entities,
              named_entities_count,
              sci_markers_total_count, found_sci_dms, markers_counts,
              topic_intro_dm_count, topic_intro_dm_in_ord, topic_intro_dm_freq,
              info_sequence_count, info_sequence_in_ord, info_sequence_freq,
              illustration_dm_count, illustration_dm_in_ord, illustration_dm_freq,
              material_sequence_count, material_sequence_in_ord, material_sequence_freq,
              conclusion_dm_count, conclusion_dm_in_ord, conclusion_dm_freq,
              intro_new_addit_info_count, intro_new_addit_info_in_ord, intro_new_addit_info_freq,
              info_explanation_or_repetition_count, info_explanation_or_repetition_in_ord,
              info_explanation_or_repetition_freq,
              contrast_dm_count, contrast_dm_in_ord, contrast_dm_freq,
              examples_introduction_dm_count, examples_introduction_dm_in_ord,
              examples_introduction_dm_freq,
              author_opinion_count, author_opinion_in_ord, author_opinion_freq,
              categorical_attitude_dm_count, categorical_attitude_dm_in_ord, categorical_attitude_dm_freq,
              less_categorical_attitude_dm_count, less_categorical_attitude_dm_in_ord,
              less_categorical_attitude_dm_freq,
              call_to_action_dm_count, call_to_action_dm_in_ord, call_to_action_dm_freq,
              joint_action_count, joint_action_in_ord, joint_action_freq,
              putting_emphasis_dm_count, putting_emphasis_dm_in_ord, putting_emphasis_dm_freq,
              refer_to_background_knowledge_count, refer_to_background_knowledge_in_ord,
              refer_to_background_knowledge_freq
              ))
        self.connection.commit()

    def insert_interference_features(self, pos_unigrams_counts, pos_unigrams_freq, pos_bigrams_counts,
                                     pos_bigrams_freq, pos_trigrams_counts, pos_trigrams_freq,
                                     char_unigram_counts, char_unigram_freq, char_bigram_counts,
                                     char_bigram_freq, char_trigram_counts, char_trigram_freq,
                                     token_positions_normalized_frequencies, token_positions_counts,
                                     token_positions_in_sent, func_w_trigrams_freqs, func_w_trigram_with_pos_counts,
                                     func_w_full_contexts):
        """Вставка данных в таблицу Interference_features"""
        self.cursor.execute('''
        INSERT INTO Interference_features (pos_unigrams_counts, pos_unigrams_freq, pos_bigrams_counts, 
                                           pos_bigrams_freq, pos_trigrams_counts, pos_trigrams_freq, 
                                           char_unigram_counts, char_unigram_freq, char_bigram_counts, 
                                           char_bigram_freq, char_trigram_counts, char_trigram_freq, 
                                           token_positions_normalized_frequencies, 
                                           token_positions_counts, token_positions_in_sent, func_w_trigrams_freqs, 
                                           func_w_trigram_with_pos_counts, 
                                           func_w_full_contexts)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (pos_unigrams_counts, pos_unigrams_freq, pos_bigrams_counts, pos_bigrams_freq,
              pos_trigrams_counts, pos_trigrams_freq, char_unigram_counts, char_unigram_freq,
              char_bigram_counts, char_bigram_freq, char_trigram_counts, char_trigram_freq,
              token_positions_normalized_frequencies, token_positions_counts, token_positions_in_sent,
              func_w_trigrams_freqs, func_w_trigram_with_pos_counts, func_w_full_contexts))
        self.connection.commit()

    def insert_miscellaneous_features(self, func_words_freq, func_words_counts, pronoun_frequencies, pronoun_counts,
                                      punct_marks_normalized_frequency, punct_marks_to_all_punct_frequency,
                                      punctuation_counts, passive_to_all_v_ratio,
                                      passive_verbs, passive_verbs_count, all_verbs, all_verbs_count,
                                      readability_index):
        """Вставка данных в таблицу Miscellaneous_features"""
        self.cursor.execute('''
        INSERT INTO Miscellaneous_features (func_words_freq, func_words_counts, pronoun_frequencies, pronoun_counts,
         punct_marks_normalized_frequency, punct_marks_to_all_punct_frequency, punctuation_counts, passive_to_all_v_ratio,
         passive_verbs, passive_verbs_count, all_verbs, all_verbs_count, readability_index)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (func_words_freq, func_words_counts, pronoun_frequencies, pronoun_counts,
              punct_marks_normalized_frequency, punct_marks_to_all_punct_frequency, punctuation_counts,
              passive_to_all_v_ratio, passive_verbs, passive_verbs_count, all_verbs, all_verbs_count,
              readability_index))
        self.connection.commit()

    def insert_text_passport(self, text, title, subject_area, keywords, publication_year, published_in,
                             authors, author_gender, author_birth_year):
        """Вставка данных в таблицу Text_Passport"""
        self.cursor.execute('''
        INSERT INTO Text_Passport (text, title, subject_area, keywords, publication_year, published_in,
         authors, author_gender, author_birth_year)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (text, title, subject_area, keywords, publication_year, published_in,
              authors, author_gender, author_birth_year))
        self.connection.commit()

    def fetch_text_passport(self, text_id=None):
        """Извлечение данных паспорта текста из базы данных.

        :param text_id: (int или None) ID текста, для которого нужно извлечь данные.
                        Если None, извлекаются все данные.
        :return: Данные паспорта текста в виде списка кортежей.
        """
        self.cursor = self.connection.cursor()
        if text_id is None:
            self.cursor.execute("SELECT * FROM text_passport")
        else:
            self.cursor.execute("SELECT * FROM text_passport WHERE text_id = ?", (text_id,))
        return self.cursor.fetchall()

    def display_simplification_analysis(self, text_id):
        """Извлечение и отображение результатов анализа упрощения текста по его ID."""
        self.cursor.execute("""
            SELECT lexical_density, ttr_lex_variety, log_ttr_lex_variety, modified_lex_variety,
                   mean_word_length, syllable_ratio, total_syllables_count, tokens_mean_sent_length,
                   chars_mean_sent_length, mean_word_rank_1, mean_word_rank_2, most_freq_words
            FROM Simplification_features
            WHERE text_id = ?
        """, (text_id,))

        simplification_data = self.cursor.fetchone()

        if simplification_data:
            (lexical_density, ttr_lex_variety, log_ttr_lex_variety, modified_lex_variety,
             mean_word_length, syllable_ratio, total_syllables_count, tokens_mean_sent_length,
             chars_mean_sent_length, mean_word_rank_1, mean_word_rank_2, most_freq_words) = simplification_data

            print("\n" + Fore.LIGHTWHITE_EX + "*" * 80)
            print(
                Fore.LIGHTYELLOW_EX + Style.BRIGHT + "                 РЕЗУЛЬТАТЫ АНАЛИЗА" + Fore.LIGHTRED_EX +
                " SIMPLIFICATION" + Fore.LIGHTYELLOW_EX + f" ДЛЯ ТЕКСТА {text_id}")
            print(Fore.LIGHTWHITE_EX + "*" * 80)
            wait_for_enter_to_analyze()

            table = Table()

            table.add_column("Показатель", no_wrap=True, style="bold")
            table.add_column("Значение", min_width=30)

            table.add_row("Лексическая плотность", f"{lexical_density:.2f}%")
            table.add_row("\nЛексическая вариативность (TTR)", f"\n{ttr_lex_variety:.2f}%")
            table.add_row("Логарифмический TTR", f"{log_ttr_lex_variety:.2f}%")
            table.add_row("Лексич. вариативность на основе\nуникальных типов", f"{modified_lex_variety:.2f}")
            table.add_row("\nСредняя длина слов в символах", f"\n{mean_word_length:.2f}")
            table.add_row("Средняя длина слов в слогах", f"{syllable_ratio:.2f}")
            table.add_row("Общее количество слогов", f"{total_syllables_count}")
            table.add_row("\nСредняя длина предложений в токенах", f"\n{tokens_mean_sent_length:.2f}")
            table.add_row("Средняя длина предложений в символах", f"{chars_mean_sent_length:.2f}")
            table.add_row("\nСредний ранг слов (1)", f"\n{mean_word_rank_1:.2f}")
            table.add_row("\nСредний ранг слов (2)", f"\n{mean_word_rank_1:.2f}")

            # Заменяем одинарные кавычки на двойные и удаляем возможные невалидные символы
            json_str = most_freq_words.replace("'", '"').strip()

            # Преобразуем ключи в строки
            json_str = re.sub(r'(\d+):', r'"\1":', json_str)
            # Преобразуем строку most_freq_words в словарь
            try:
                most_freq_words_dict = json.loads(json_str)
            except json.JSONDecodeError as e:
                print(Fore.LIGHTRED_EX + Style.BRIGHT + f"Ошибка парсинга JSON: {e}" + Fore.RESET)
                return

            if "50" in most_freq_words_dict:
                top_50_words = list(most_freq_words_dict["50"].items())
                top_50_words_str = ', '.join([f"{word} ({freq:.3f})" for word, freq in top_50_words])
                table.add_row("\nНаиболее частотные 50 слов \n(и их нормализованные частоты)", '\n' + top_50_words_str)
            else:
                table.add_row("\nНаиболее частотные 50 слов \n(и их нормализованные частоты)", "\nНет данных")

            console.print(table)
        else:
            print(
                Fore.LIGHTRED_EX + Style.BRIGHT + "Результаты анализа SIMPLIFICATION для этого текста не найдены." +
                Fore.RESET)

    def display_normalisation_analysis(self, text_id):
        """Извлечение и отображение результатов анализа индикаторов универсалии Normalisation по его ID."""
        self.cursor.execute("""
            SELECT repetition, repeated_content_words_count, repeated_content_words, total_word_tokens
            FROM Normalisation_features
            WHERE text_id = ?
        """, (text_id,))

        normalisation_data = self.cursor.fetchone()

        if normalisation_data:
            (repetition, repeated_content_words_count, repeated_content_words, total_word_tokens) = normalisation_data

            print("\n" + Fore.LIGHTWHITE_EX + "*" * 80)
            print(
                Fore.LIGHTYELLOW_EX + Style.BRIGHT + "                 РЕЗУЛЬТАТЫ АНАЛИЗА" + Fore.LIGHTRED_EX +
                " NORMALISATION" + Fore.LIGHTYELLOW_EX + f" ДЛЯ ТЕКСТА {text_id}")
            print(Fore.LIGHTWHITE_EX + "*" * 80)

            table = Table()

            table.add_column("Показатель", no_wrap=True, style="bold")
            table.add_column("Значение", justify="center", min_width=20)

            table.add_row("Повторяемость", f"{repetition:.2f}%")
            table.add_row("Число повторяющихся знаменательных слов", f"{repeated_content_words}")
            table.add_row("Всего токенов", f"{total_word_tokens}")
            console.print(table)
            wait_for_enter_to_analyze()

            print_word_occurrences_table(repeated_content_words_count)
        else:
            print(
                Fore.LIGHTRED_EX + Style.BRIGHT + "Результаты анализа нормализации для этого текста не найдены." +
                Fore.RESET)

    def display_explicitation_analysis(self, text_id):
        """Извлечение и отображение результатов анализа индикаторов универсалии Explicitation по его ID."""
        self.cursor.execute("""
            SELECT explicit_naming_ratio, single_naming, mean_multiple_naming, single_entities,
                   single_entities_count, multiple_entities, multiple_entities_count, named_entities,
                   named_entities_count,
                   sci_markers_total_count, markers_counts,
                   topic_intro_dm_count, topic_intro_dm_in_ord, topic_intro_dm_freq,
                   info_sequence_count, info_sequence_in_ord, info_sequence_freq,
                   illustration_dm_count, illustration_dm_in_ord, illustration_dm_freq,
                   material_sequence_count, material_sequence_in_ord, material_sequence_freq,
                   conclusion_dm_count, conclusion_dm_in_ord, conclusion_dm_freq,
                   intro_new_addit_info_count, intro_new_addit_info_in_ord, intro_new_addit_info_freq,
                   info_explanation_or_repetition_count, info_explanation_or_repetition_in_ord, info_explanation_or_repetition_freq,
                   contrast_dm_count, contrast_dm_in_ord, contrast_dm_freq,
                   examples_introduction_dm_count, examples_introduction_dm_in_ord, examples_introduction_dm_freq,
                   author_opinion_count, author_opinion_in_ord, author_opinion_freq,
                   categorical_attitude_dm_count, categorical_attitude_dm_in_ord, categorical_attitude_dm_freq,
                   less_categorical_attitude_dm_count, less_categorical_attitude_dm_in_ord, less_categorical_attitude_dm_freq,
                   call_to_action_dm_count, call_to_action_dm_in_ord, call_to_action_dm_freq,
                   joint_action_count, joint_action_in_ord, joint_action_freq,
                   putting_emphasis_dm_count, putting_emphasis_dm_in_ord, putting_emphasis_dm_freq,
                   refer_to_background_knowledge_count, refer_to_background_knowledge_in_ord, refer_to_background_knowledge_freq
            FROM Explicitation_features
            WHERE text_id = ?
        """, (text_id,))

        explicitation_data = self.cursor.fetchone()

        if explicitation_data:
            (explicit_naming_ratio, single_naming, mean_multiple_naming, single_entities,
             single_entities_count, multiple_entities, multiple_entities_count, named_entities,
             named_entities_count,
             sci_markers_total_count, markers_counts,
             topic_intro_dm_count, topic_intro_dm_in_ord, topic_intro_dm_freq,
             info_sequence_count, info_sequence_in_ord, info_sequence_freq,
             illustration_dm_count, illustration_dm_in_ord, illustration_dm_freq,
             material_sequence_count, material_sequence_in_ord, material_sequence_freq,
             conclusion_dm_count, conclusion_dm_in_ord, conclusion_dm_freq,
             intro_new_addit_info_count, intro_new_addit_info_in_ord, intro_new_addit_info_freq,
             info_explanation_or_repetition_count, info_explanation_or_repetition_in_ord,
             info_explanation_or_repetition_freq,
             contrast_dm_count, contrast_dm_in_ord, contrast_dm_freq,
             examples_introduction_dm_count, examples_introduction_dm_in_ord, examples_introduction_dm_freq,
             author_opinion_count, author_opinion_in_ord, author_opinion_freq,
             categorical_attitude_dm_count, categorical_attitude_dm_in_ord, categorical_attitude_dm_freq,
             less_categorical_attitude_dm_count, less_categorical_attitude_dm_in_ord, less_categorical_attitude_dm_freq,
             call_to_action_dm_count, call_to_action_dm_in_ord, call_to_action_dm_freq,
             joint_action_count, joint_action_in_ord, joint_action_freq,
             putting_emphasis_dm_count, putting_emphasis_dm_in_ord, putting_emphasis_dm_freq,
             refer_to_background_knowledge_count, refer_to_background_knowledge_in_ord,
             refer_to_background_knowledge_freq) = explicitation_data

            print("\n" + Fore.LIGHTWHITE_EX + "*" * 80)
            print(
                Fore.LIGHTYELLOW_EX + Style.BRIGHT + "                 РЕЗУЛЬТАТЫ АНАЛИЗА" + Fore.LIGHTRED_EX +
                " EXPLICITATION" + Fore.LIGHTYELLOW_EX + f" ДЛЯ ТЕКСТА {text_id}")
            print(Fore.LIGHTWHITE_EX + "*" * 80)

            table = Table()

            table.add_column("Показатель", style="bold")
            table.add_column("Значение", justify="center", min_width=30)

            table.add_row("Explicit naming", f"{explicit_naming_ratio:.2f}%")
            table.add_row("Single naming", f"{single_naming:.2f}%")
            table.add_row("Средняя длина именованных сущностей \n(в токенах)", f"{mean_multiple_naming:.2f}")

            # Выводим таблицу
            console.print(table)
            wait_for_enter_to_analyze()
            display_entities(named_entities, named_entities_count)
            wait_for_enter_to_analyze()
            print_dm_analysis_results(sci_markers_total_count, markers_counts,
                                      topic_intro_dm_count, topic_intro_dm_in_ord, topic_intro_dm_freq,
                                      info_sequence_count, info_sequence_in_ord, info_sequence_freq,
                                      illustration_dm_count, illustration_dm_in_ord, illustration_dm_freq,
                                      material_sequence_count, material_sequence_in_ord, material_sequence_freq,
                                      conclusion_dm_count, conclusion_dm_in_ord, conclusion_dm_freq,
                                      intro_new_addit_info_count, intro_new_addit_info_in_ord,
                                      intro_new_addit_info_freq,
                                      info_explanation_or_repetition_count, info_explanation_or_repetition_in_ord,
                                      info_explanation_or_repetition_freq,
                                      contrast_dm_count, contrast_dm_in_ord, contrast_dm_freq,
                                      examples_introduction_dm_count, examples_introduction_dm_in_ord,
                                      examples_introduction_dm_freq,
                                      author_opinion_count, author_opinion_in_ord, author_opinion_freq,
                                      categorical_attitude_dm_count, categorical_attitude_dm_in_ord,
                                      categorical_attitude_dm_freq,
                                      less_categorical_attitude_dm_count, less_categorical_attitude_dm_in_ord,
                                      less_categorical_attitude_dm_freq,
                                      call_to_action_dm_count, call_to_action_dm_in_ord, call_to_action_dm_freq,
                                      joint_action_count, joint_action_in_ord, joint_action_freq,
                                      putting_emphasis_dm_count, putting_emphasis_dm_in_ord, putting_emphasis_dm_freq,
                                      refer_to_background_knowledge_count, refer_to_background_knowledge_in_ord,
                                      refer_to_background_knowledge_freq)
        else:
            print(
                Fore.LIGHTRED_EX + Style.BRIGHT + "Результаты анализа экспликации для этого текста не найдены." +
                Fore.RESET)

    def display_interference_analysis(self, text_id):
        """Извлечение и отображение результатов анализа индикаторов универсалии Interference по его ID."""
        self.cursor.execute("""
            SELECT pos_unigrams_counts, pos_unigrams_freq, pos_bigrams_counts, pos_bigrams_freq, 
                   pos_trigrams_counts, pos_trigrams_freq, char_unigram_counts, char_unigram_freq,
                   char_bigram_counts, char_bigram_freq, char_trigram_counts, char_trigram_freq, 
                   token_positions_counts, token_positions_normalized_frequencies, token_positions_in_sent, 
                   func_w_trigrams_freqs, func_w_trigram_with_pos_counts, func_w_full_contexts
            FROM Interference_features
            WHERE text_id = ?
        """, (text_id,))

        interference_data = self.cursor.fetchone()

        if interference_data:
            (pos_unigrams_counts, pos_unigrams_freq, pos_bigrams_counts, pos_bigrams_freq,
             pos_trigrams_counts, pos_trigrams_freq, char_unigram_counts, char_unigram_freq,
             char_bigram_counts, char_bigram_freq, char_trigram_counts, char_trigram_freq,
             token_positions_counts, token_positions_normalized_frequencies, token_positions_in_sent,
             func_w_trigrams_freqs, func_w_trigram_with_pos_counts, func_w_full_contexts) = interference_data

            print("\n" + Fore.LIGHTWHITE_EX + "*" * 80)
            print(
                Fore.LIGHTYELLOW_EX + Style.BRIGHT + "                 РЕЗУЛЬТАТЫ АНАЛИЗА" + Fore.LIGHTRED_EX +
                " INTERFERENCE" + Fore.LIGHTYELLOW_EX + f" ДЛЯ ТЕКСТА {text_id}")
            print(Fore.LIGHTWHITE_EX + "*" * 80)

            print(Fore.LIGHTYELLOW_EX + Style.BRIGHT + "\n                      ЧАСТОТЫ ЧАСТЕРЕЧНЫХ N-ГРАММОВ")
            display_ngrams_summary(pos_unigrams_counts, pos_unigrams_freq, pos_bigrams_counts, pos_bigrams_freq,
                                   pos_trigrams_counts, pos_trigrams_freq)

            print(Fore.LIGHTYELLOW_EX + Style.BRIGHT + "\n                      ЧАСТОТЫ БУКВЕННЫХ N-ГРАММОВ")
            display_ngrams_summary(char_unigram_counts, char_unigram_freq, char_bigram_counts, char_bigram_freq,
                                   char_trigram_counts, char_trigram_freq)

            print(Fore.LIGHTYELLOW_EX + Style.BRIGHT + "\n                      ПОЗИЦИОННАЯ ЧАСТОТА ТОКЕНОВ")
            print(Fore.LIGHTGREEN_EX + Style.BRIGHT + "Учитываются предложения, длина которых больше 5 токенов.")

            print_frequencies(token_positions_normalized_frequencies, token_positions_counts)
            print(
                Fore.LIGHTYELLOW_EX + Style.BRIGHT + "\n             ТОКЕНЫ И ИХ ЧАСТИ РЕЧИ НА РАЗНЫХ ПОЗИЦИЯХ В ПРЕДЛОЖЕНИИ"
                + Fore.RESET)
            print(
                Fore.LIGHTGREEN_EX + Style.BRIGHT + "* Выводятся контексты предложений, длиннее 5 токенов."
                + Fore.RESET)
            wait_for_enter_to_analyze()
            print_positions(token_positions_in_sent)
            print_trigram_tables_with_func_w(func_w_trigrams_freqs, func_w_trigram_with_pos_counts,
                                             func_w_full_contexts)
        else:
            print(
                Fore.LIGHTRED_EX + Style.BRIGHT + "Результаты анализа интерференции для этого текста не найдены."
                + Fore.RESET)

    def display_miscellaneous_features_analysis(self, text_id):

        self.cursor.execute("""
            SELECT func_words_freq, func_words_counts, pronoun_frequencies,pronoun_counts, 
            punct_marks_normalized_frequency, punct_marks_to_all_punct_frequency,punctuation_counts, 
            passive_to_all_v_ratio, passive_verbs, passive_verbs_count, all_verbs, all_verbs_count, readability_index
            FROM Miscellaneous_features
            WHERE text_id = ?
        """, (text_id,))

        miscellaneous_features_data = self.cursor.fetchone()

        if miscellaneous_features_data:
            (func_words_freq, func_words_counts, pronoun_frequencies, pronoun_counts, punct_marks_normalized_frequency,
             punct_marks_to_all_punct_frequency, punctuation_counts, passive_to_all_v_ratio,
             passive_verbs, passive_verbs_count, all_verbs, all_verbs_count,
             readability_index) = miscellaneous_features_data

            print("\n" + Fore.LIGHTWHITE_EX + "*" * 80)
            print(
                Fore.LIGHTYELLOW_EX + Style.BRIGHT + "              РЕЗУЛЬТАТЫ АНАЛИЗА" + Fore.LIGHTRED_EX +
                " ОСТАЛЬНЫХ ИНДИКАТОРОВ" + Fore.LIGHTYELLOW_EX + f" ДЛЯ ТЕКСТА {text_id}")
            print(Fore.LIGHTWHITE_EX + "*" * 80)
            wait_for_enter_to_analyze()

            print_func_w__frequencies(func_words_freq, func_words_counts)
            wait_for_enter_to_analyze()

            print_pronoun_frequencies(pronoun_frequencies, pronoun_counts)
            wait_for_enter_to_analyze()
            display_punctuation_analysis(punct_marks_normalized_frequency, punct_marks_to_all_punct_frequency,
                                         punctuation_counts)
            wait_for_enter_to_analyze()
            print_passive_verbs_ratio(passive_to_all_v_ratio,
                                      passive_verbs, passive_verbs_count, all_verbs, all_verbs_count)
            display_readability_index(readability_index)

        else:
            print(
                Fore.LIGHTRED_EX + Style.BRIGHT + "Результаты анализа остальных индикаторов для этого текста не "
                                                  "найдены." + Fore.RESET)

    def display_morphological_annotation(self, text_id):
        """Отображает морфологическую разметку текста по его ID."""
        self.cursor.execute("""
            SELECT morph_annotation FROM Morphological_annotation WHERE text_id = ?
        """, (text_id,))
        result = self.cursor.fetchone()
        if result:
            # Преобразуем строку JSON в объект Python
            sentences_info = json.loads(result[0])
            display_morphological_annotation(sentences_info)

    def display_simplification_features_for_corpus(self):
        """Отображает средние показатели индикаторов универсалии Simplification."""
        # Выполняем запрос на извлечение средних значений
        self.cursor.execute('''
            SELECT 
                AVG(lexical_density), 
                AVG(ttr_lex_variety), 
                AVG(log_ttr_lex_variety), 
                AVG(modified_lex_variety), 
                AVG(mean_word_length), 
                AVG(syllable_ratio), 
                AVG(total_syllables_count), 
                AVG(tokens_mean_sent_length), 
                AVG(chars_mean_sent_length), 
                AVG(mean_word_rank_1),
                AVG(mean_word_rank_2)
            FROM Simplification_features
        ''')

        result = self.cursor.fetchone()

        if result:
            (avg_lexical_density, avg_ttr_lex_variety, avg_log_ttr_lex_variety, avg_modified_lex_variety,
             avg_mean_word_length, avg_syllable_ratio, avg_total_syllables_count, avg_tokens_mean_sent_length,
             avg_chars_mean_sent_length, avg_mean_word_rank_1, avg_mean_word_rank_2) = result

            print("\n" + Fore.LIGHTWHITE_EX + "*" * 80)
            print(
                Fore.LIGHTYELLOW_EX + Style.BRIGHT + '             СРЕДНИЕ ПОКАЗАТЕЛИ УНИВЕРСАЛИИ' +
                Fore.LIGHTRED_EX + Style.BRIGHT + ' SIMPLIFICATION')
            print(Fore.LIGHTWHITE_EX + "*" * 80)
            table = Table()

            table.add_column("Индикатор", justify="left", no_wrap=True, style="bold")
            table.add_column("Значение", justify="center", min_width=15)

            table.add_row("Лексическая плотность", f"{avg_lexical_density:.2f}%")
            table.add_row("\nЛексическая вариативность (TTR)", f"\n{avg_ttr_lex_variety:.2f}%")
            table.add_row("Логарифмический TTR", f"{avg_log_ttr_lex_variety:.2f}%")
            table.add_row("Лексич. вариативность на основе\nуникальных типов", f"{avg_modified_lex_variety:.2f}")
            table.add_row("\nСредняя длина слова (в символах)", f"\n{avg_mean_word_length:.2f}")
            table.add_row("Средняя длина слов (в слогах)", f"{avg_syllable_ratio:.2f}")
            table.add_row("Общее количество слогов", f"{avg_total_syllables_count:.0f}")
            table.add_row("\nСредняя длина предложений (в токенах)", f"\n{avg_tokens_mean_sent_length:.2f}")
            table.add_row("Средняя длина предложений (в символах)", f"{avg_chars_mean_sent_length:.2f}")
            table.add_row("\nСредний ранг слов (1)", f"\n{avg_mean_word_rank_1:.2f}")
            table.add_row("Средний ранг слов (2)", f"{avg_mean_word_rank_2:.2f}")

            console.print(table)
            print(Fore.LIGHTWHITE_EX + "*" * 80)
            wait_for_enter_to_choose_opt()
        else:
            print(Fore.LIGHTRED_EX + "Данные о показателях Simplification отсутствуют." + Fore.RESET)

    def display_normalisation_features_for_corpus(self):
        """Отображение средних значений индикаторов универсалии Normalisation"""
        self.cursor.execute(
            'SELECT AVG(repetition), AVG(repeated_content_words), AVG(total_word_tokens) FROM Normalisation_features')
        result = self.cursor.fetchone()

        if result:
            avg_repetition, avg_repeated_content_words, avg_total_word_tokens = result

            print("\n" + Fore.LIGHTWHITE_EX + "*" * 80)
            print(
                Fore.LIGHTYELLOW_EX + Style.BRIGHT + '            СРЕДНИЕ ПОКАЗАТЕЛИ УНИВЕРСАЛИИ' +
                Fore.LIGHTRED_EX + Style.BRIGHT + ' NORMALISATION')
            print(Fore.LIGHTWHITE_EX + "*" * 80)
            table = Table()

            table.add_column("Показатель", justify="left", no_wrap=True, style="bold")
            table.add_column("Значение", justify="center")

            table.add_row("Повторяемость", f"{avg_repetition:.2f}%")
            table.add_row("Количество повторяющихся знаменательных слов", f"{avg_repeated_content_words:.2f}")
            table.add_row("Количество словарных токенов", f"{avg_total_word_tokens:.2f}")

            console.print(table)
            wait_for_enter_to_analyze()

    def display_explicitation_features_for_corpus(self):
        """Отображает средние показатели индикаторов универсалии Explicitation"""
        self.cursor.execute('''
            SELECT 
                AVG(explicit_naming_ratio),
                AVG(single_naming),
                AVG(mean_multiple_naming),
                AVG(single_entities_count),
                AVG(multiple_entities_count),
                AVG(named_entities_count),
                AVG(sci_markers_total_count),

                AVG(topic_intro_dm_count),
                AVG(topic_intro_dm_freq),

                AVG(info_sequence_count),
                AVG(info_sequence_freq),

                AVG(illustration_dm_count),
                AVG(illustration_dm_freq),

                AVG(material_sequence_count),
                AVG(material_sequence_freq),

                AVG(conclusion_dm_count),
                AVG(conclusion_dm_freq),

                AVG(intro_new_addit_info_count),
                AVG(intro_new_addit_info_freq),

                AVG(info_explanation_or_repetition_count),
                AVG(info_explanation_or_repetition_freq),

                AVG(contrast_dm_count),
                AVG(contrast_dm_freq),

                AVG(examples_introduction_dm_count),
                AVG(examples_introduction_dm_freq),

                AVG(author_opinion_count),
                AVG(author_opinion_freq),

                AVG(categorical_attitude_dm_count),
                AVG(categorical_attitude_dm_freq),

                AVG(less_categorical_attitude_dm_count),
                AVG(less_categorical_attitude_dm_freq),

                AVG(call_to_action_dm_count),
                AVG(call_to_action_dm_freq),

                AVG(joint_action_count),
                AVG(joint_action_freq),

                AVG(putting_emphasis_dm_count),
                AVG(putting_emphasis_dm_freq),

                AVG(refer_to_background_knowledge_count),
                AVG(refer_to_background_knowledge_freq)
            FROM Explicitation_features
        ''')

        result = self.cursor.fetchone()

        if result:
            (
                avg_explicit_naming_ratio, avg_single_naming, avg_mean_multiple_naming, avg_single_entities_count,
                avg_multiple_entities_count, avg_named_entities_count, avg_sci_markers_total_count,
                avg_topic_intro_dm_count, avg_topic_intro_dm_freq, avg_info_sequence_count, avg_info_sequence_freq,
                avg_illustration_dm_count, avg_illustration_dm_freq, avg_material_sequence_count,
                avg_material_sequence_freq, avg_conclusion_dm_count, avg_conclusion_dm_freq,
                avg_intro_new_addit_info_count, avg_intro_new_addit_info_freq, avg_info_explanation_or_repetition_count,
                avg_info_explanation_or_repetition_freq, avg_contrast_dm_count, avg_contrast_dm_freq,
                avg_examples_introduction_dm_count, avg_examples_introduction_dm_freq, avg_author_opinion_count,
                avg_author_opinion_freq, avg_categorical_attitude_dm_count, avg_categorical_attitude_dm_freq,
                avg_less_categorical_attitude_dm_count, avg_less_categorical_attitude_dm_freq,
                avg_call_to_action_dm_count,
                avg_call_to_action_dm_freq, avg_joint_action_count, avg_joint_action_freq,
                avg_putting_emphasis_dm_count,
                avg_putting_emphasis_dm_freq, avg_refer_to_background_knowledge_count,
                avg_refer_to_background_knowledge_freq
            ) = result

            print("\n" + Fore.LIGHTWHITE_EX + "*" * 80)
            print(
                Fore.LIGHTYELLOW_EX + Style.BRIGHT + '              СРЕДНИЕ ПОКАЗАТЕЛИ УНИВЕРСАЛИИ'
                + Fore.LIGHTRED_EX + Style.BRIGHT + ' EXPLICITATION')
            print(Fore.LIGHTWHITE_EX + "*" * 80)

            table = Table()

            # Добавляем колонки
            table.add_column("Индикатор", justify="left", no_wrap=True, style="bold")
            table.add_column("Значение", justify="center")

            # Заполняем таблицу данными
            table.add_row("Explicit naming", f"{avg_explicit_naming_ratio:.2f}%")
            table.add_row("Single naming", f"{avg_single_naming:.2f}%")
            table.add_row("Средняя длина именованных сущностей (в токенах)", f"{avg_mean_multiple_naming:.2f}")
            table.add_row("Количество именованных сущностей", f"{avg_named_entities_count:.2f}")
            console.print(table)
            wait_for_enter_to_analyze()

            print(
                Fore.LIGHTYELLOW_EX + Style.BRIGHT + "\n           СРЕДНИЕ ПОКАЗАТЕЛИ ЧАСТОТ ДИСКУРСИВНЫХ МАРКЕРОВ "
                                             "ПО КАТЕГОРИЯМ" + Fore.RESET)
            print(
                Fore.BLUE + Style.DIM + f"                        В среднем тексты содержат "
                                        f"{avg_sci_markers_total_count:.0F} ДМ" + Fore.RESET)

            freq_table = Table()
            freq_table.add_column("Категория ДМ\n", justify="left", no_wrap=True)
            freq_table.add_column("Абсолютная частота\n", justify="center")
            freq_table.add_column("Нормализованная частота (%)", justify="center")

            frequency_data = [
                ("Введение в тему", avg_topic_intro_dm_count, avg_topic_intro_dm_freq),
                ("Порядок следования информации", avg_info_sequence_count, avg_info_sequence_freq),
                ("Иллюстративный материал", avg_illustration_dm_count, avg_illustration_dm_freq),
                ("Порядок расположения материала", avg_material_sequence_count, avg_material_sequence_freq),
                ("Вывод/заключение", avg_conclusion_dm_count, avg_conclusion_dm_freq),
                ("Введение новой/доп. информации", avg_intro_new_addit_info_count, avg_intro_new_addit_info_freq),
                ("Повтор/конкретизация информации", avg_info_explanation_or_repetition_count,
                 avg_info_explanation_or_repetition_freq),
                ("Противопоставление", avg_contrast_dm_count, avg_contrast_dm_freq),
                ("Введение примеров", avg_examples_introduction_dm_count, avg_examples_introduction_dm_freq),
                ("Мнение автора", avg_author_opinion_count, avg_author_opinion_freq),
                ("Категоричная оценка", avg_categorical_attitude_dm_count, avg_categorical_attitude_dm_freq),
                ("Менее категоричная оценка", avg_less_categorical_attitude_dm_count,
                 avg_less_categorical_attitude_dm_freq),
                ("Призыв к действию", avg_call_to_action_dm_count, avg_call_to_action_dm_freq),
                ("Совместное действие", avg_joint_action_count, avg_joint_action_freq),
                ("Акцентирование внимания", avg_putting_emphasis_dm_count, avg_putting_emphasis_dm_freq),
                ("Отсылка к фоновым знаниям", avg_refer_to_background_knowledge_count,
                 avg_refer_to_background_knowledge_freq),
            ]

            # Фильтрация по частоте > 0
            frequency_data_filtered = [(cat, count, freq) for cat, count, freq in frequency_data if count > 0]

            # Сортировка по абсолютной частоте в порядке убывания
            frequency_data_sorted = sorted(frequency_data_filtered, key=lambda x: x[1], reverse=True)

            # Добавление строк в таблицу после сортировки
            for category_name, count, freq in frequency_data_sorted:
                freq_table.add_row(category_name, f"{count:.3f}", f"{freq:.3f}%")

            # Выводим таблицу
            console.print(freq_table)
            wait_for_enter_to_choose_opt()

    def display_miscellaneous_features_for_corpus(self):
        """Отображение средних показателей индикаторов  Miscellaneous_features."""
        # Извлечение агрегированных данных для количественных показателей
        self.cursor.execute('''
                SELECT AVG(passive_to_all_v_ratio) AS avg_passive_to_all_v_ratio, 
                       AVG(passive_verbs_count) AS avg_passive_verbs_count, 
                       AVG(all_verbs_count) AS avg_all_verbs_count, 
                       AVG(readability_index) AS avg_readability_index
                FROM Miscellaneous_features
            ''')
        result_aggregated = self.cursor.fetchone()

        if result_aggregated:
            avg_passive_to_all_v_ratio, avg_passive_verbs_count, avg_all_verbs_count, avg_readability_index = result_aggregated

            print("\n" + Fore.LIGHTWHITE_EX + "*" * 80)
            print(
                Fore.LIGHTYELLOW_EX + Style.BRIGHT + '      СРЕДНИЕ ПОКАЗАТЕЛИ ОСТАЛЬНЫХ ИНДИКАТОРОВ УНИВЕРСАЛИИ' +
                Fore.LIGHTRED_EX + Style.BRIGHT + ' EXPLICITATION')
            print(Fore.LIGHTWHITE_EX + "*" * 80)

            table = Table()
            table.add_column("Показатель", justify="left", style="bold")
            table.add_column("Значение", justify="center", min_width=15)

            table.add_row("Отношение пассивных глаголов\nко всем глаголам (%)", f"{avg_passive_to_all_v_ratio:.3f}%")
            table.add_row("Пассивные глаголы", f"{avg_passive_verbs_count:.2f}")
            table.add_row("Все глаголы", f"{avg_all_verbs_count:.2f}")
            table.add_row("\nИндекс читаемости по Флешу", f"\n{avg_readability_index:.3f}")

            console.print(table)
            wait_for_enter_to_analyze()

        # Извлечение данных для частот служебных слов и знаков препинания
        self.cursor.execute('''
                SELECT func_words_freq, 
                       func_words_counts,
                       punct_marks_normalized_frequency, 
                       punct_marks_to_all_punct_frequency,
                       punctuation_counts,
                       pronoun_frequencies,
                       pronoun_counts
                FROM Miscellaneous_features
            ''')
        result_json = self.cursor.fetchall()

        if result_json:
            # Инициализация накопителей для агрегированных данных
            func_words_freq_accum = defaultdict(float)
            func_words_counts_accum = defaultdict(int)

            punct_normalized_accum = defaultdict(float)
            punct_to_all_accum = defaultdict(float)
            punctuation_counts_accum = defaultdict(int)
            pronoun_freq_accum = defaultdict(float)
            pronoun_counts_accum = defaultdict(int)

            count_entries = len(result_json)

            for row in result_json:
                (func_words_freq_json, func_words_counts_json, punct_norm_json,
                 punct_to_all_json, punctuation_counts_json, pronoun_freq, pronoun_counts) = row

                # Обрабатываем JSON-поля и добавляем их значения к накопителям
                func_words_freq = json.loads(func_words_freq_json)
                func_words_counts = json.loads(func_words_counts_json)
                punct_marks_normalized_frequency = json.loads(punct_norm_json)
                punct_marks_to_all_punct_frequency = json.loads(punct_to_all_json)
                punctuation_counts = json.loads(punctuation_counts_json)
                pronoun_frequencies = json.loads(pronoun_freq)
                pronoun_counts = json.loads(pronoun_counts)

                for word, freq in func_words_freq.items():
                    func_words_freq_accum[word] += freq

                for word, count in func_words_counts.items():
                    func_words_counts_accum[word] += count

                for punct, freq in punct_marks_normalized_frequency.items():
                    punct_normalized_accum[punct] += freq

                for punct, freq in punct_marks_to_all_punct_frequency.items():
                    punct_to_all_accum[punct] += freq

                for punct, count in punctuation_counts.items():
                    punctuation_counts_accum[punct] += count

                for pronoun, freq in pronoun_frequencies.items():
                    pronoun_freq_accum[pronoun] += freq

                for pronoun, count in pronoun_counts.items():
                    pronoun_counts_accum[pronoun] += count

            avg_func_words_freq = {word: freq / count_entries for word, freq in func_words_freq_accum.items()}
            avg_func_words_counts = {word: count / count_entries for word, count in func_words_counts_accum.items()}

            avg_punct_normalized_frequency = {punct: freq / count_entries for punct, freq in
                                              punct_normalized_accum.items()}
            avg_punct_to_all_punct_frequency = {punct: freq / count_entries for punct, freq in
                                                punct_to_all_accum.items()}
            avg_punctuation_counts = {punct: count / count_entries for punct, count in punctuation_counts_accum.items()}

            avg_pronoun_frequencies = {pronoun: freq / count_entries for pronoun, freq in pronoun_freq_accum.items()}
            avg_pronoun_counts = {pronoun: count / count_entries for pronoun, count in pronoun_counts_accum.items()}

            print(Fore.LIGHTYELLOW_EX + Style.BRIGHT + '\n                 СРЕДНИЕ ЧАСТОТЫ СЛУЖЕБНЫХ СЛОВ')
            wait_for_enter_to_analyze()
            table_func_words = Table()
            table_func_words.add_column("Слово\n", justify="left")
            table_func_words.add_column("Абсолютная частота\n", justify="center")
            table_func_words.add_column("Нормализованная частота\n(%)", justify="center")

            for word, freq in sorted(avg_func_words_freq.items(), key=lambda item: item[1], reverse=True):
                count = avg_func_words_counts.get(word, 0)
                table_func_words.add_row(word, str(count), f"{freq:.3f}%")

            console.print(table_func_words)
            wait_for_enter_to_analyze()

            print(Fore.LIGHTYELLOW_EX + Style.BRIGHT + '\n                  СРЕДНИЕ ЧАСТОТЫ МЕСТОИМЕНИЙ')
            table_pronouns = Table()
            table_pronouns.add_column("Местоимение\n", justify="center")
            table_pronouns.add_column("Абсолютная частота\n", justify="center")
            table_pronouns.add_column("Нормализованная частота\n(%)", justify="center")

            for pronoun, freq in sorted(avg_pronoun_frequencies.items(), key=lambda item: item[1], reverse=True):
                count = avg_pronoun_counts.get(pronoun, 0)
                table_pronouns.add_row(pronoun, str(count), f"{freq:.3f}%")

            console.print(table_pronouns)
            wait_for_enter_to_analyze()

            print(
                Fore.LIGHTYELLOW_EX + Style.BRIGHT + '\n                       СРЕДНИЕ ЧАСТОТЫ ЗНАКОВ ПРЕПИНАНИЯ')
            table_punctuation = Table()
            table_punctuation.add_column("Знак\n", justify="center")
            table_punctuation.add_column("Абсолютная частота\n", justify="center")
            table_punctuation.add_column("Частота ко всем\nтокенам текста (%)", justify="center")
            table_punctuation.add_column("Частота ко всем\nзнакам препинания (%)", justify="center")

            for punct in sorted(avg_punct_normalized_frequency.keys(),
                                key=lambda item: avg_punct_normalized_frequency[item], reverse=True):
                count = avg_punctuation_counts.get(punct, 0)
                norm_freq = avg_punct_normalized_frequency.get(punct, 0)
                all_punct_freq = avg_punct_to_all_punct_frequency.get(punct, 0)

                if norm_freq > 0 or all_punct_freq > 0:
                    table_punctuation.add_row(punct, str(count), f"{norm_freq:.2f}%", f"{all_punct_freq:.2f}%")

            console.print(table_punctuation)
            wait_for_enter_to_analyze()

        else:
            print("Нет данных для отображения.")

    def display_interference_features_for_corpus(self):
        """Отображает средние показатели для индикаторов универсалии Interference."""
        self.cursor.execute(
            "SELECT pos_unigrams_counts, pos_unigrams_freq, pos_bigrams_counts, pos_bigrams_freq, "
            "pos_trigrams_counts, pos_trigrams_freq, char_unigram_counts, char_unigram_freq, char_bigram_counts, "
            "char_bigram_freq,"
            "char_trigram_counts, char_trigram_freq, func_w_trigrams_freqs, func_w_trigram_with_pos_counts, "
            "token_positions_normalized_frequencies,"
            "token_positions_counts  FROM Interference_features")
        rows = self.cursor.fetchall()

        if not rows:
            print(Fore.LIGHTYELLOW_EX + Style.BRIGHT + "Нет данных для отображения." + Fore.RESET)
            return
        print("\n" + Fore.LIGHTWHITE_EX + "*" * 80)
        print(
            Fore.LIGHTYELLOW_EX + Style.BRIGHT + '\n              СРЕДНИЕ ПОКАЗАТЕЛИ УНИВЕРСАЛИИ' + Fore.LIGHTRED_EX +
            Style.BRIGHT + ' INTERFERENCE')
        print("\n" + Fore.LIGHTWHITE_EX + "*" * 80)

        display_grammemes()
        wait_for_enter_to_analyze()

        def min_count_choice():
            while True:
                try:
                    min_count_input = input(Fore.LIGHTGREEN_EX + Style.BRIGHT +
                                            f"Введите минимальное значение для среднего количества выводимых n-граммов"
                                            f"\nили просто нажмите 'Enter', чтобы продолжить "
                                            f"(по умолчанию значение=1): \n").strip()

                    if not min_count_input:
                        min_count = 1
                        break
                    else:
                        min_count = float(min_count_input)
                        break
                except ValueError:
                    print(Fore.LIGHTRED_EX + Style.BRIGHT + "\nОшибка! Введите числовое значение." + Fore.RESET)
            return min_count

        # Словари для накопления данных
        pos_unigrams_counts_total = defaultdict(int)
        pos_unigrams_freq_total = defaultdict(float)
        pos_bigrams_counts_total = defaultdict(int)
        pos_bigrams_freq_total = defaultdict(float)
        pos_trigrams_counts_total = defaultdict(int)
        pos_trigrams_freq_total = defaultdict(float)

        # Словари для char n-грамм
        char_unigrams_counts_total = defaultdict(int)
        char_unigrams_freq_total = defaultdict(float)
        char_bigrams_counts_total = defaultdict(int)
        char_bigrams_freq_total = defaultdict(float)
        char_trigrams_counts_total = defaultdict(int)
        char_trigrams_freq_total = defaultdict(float)

        # Словари для функциональных триграмм
        func_w_trigrams_freqs_total = defaultdict(lambda: defaultdict(float))
        func_w_trigram_with_pos_counts_total = defaultdict(lambda: defaultdict(int))

        # Словари для позиционных токенов
        token_positions_normalized_frequencies_total = defaultdict(lambda: defaultdict(float))
        token_positions_counts_total = defaultdict(lambda: defaultdict(int))

        num_texts = len(rows)  # Количество текстов

        for row in rows:
            # Десериализация POS JSON
            pos_unigrams_counts = json.loads(row[0])
            pos_unigrams_freq = json.loads(row[1])
            pos_bigrams_counts = json.loads(row[2])
            pos_bigrams_freq = json.loads(row[3])
            pos_trigrams_counts = json.loads(row[4])
            pos_trigrams_freq = json.loads(row[5])

            # Десериализация char JSON
            char_unigrams_counts = json.loads(row[6])
            char_unigrams_freq = json.loads(row[7])
            char_bigrams_counts = json.loads(row[8])
            char_bigrams_freq = json.loads(row[9])
            char_trigrams_counts = json.loads(row[10])
            char_trigrams_freq = json.loads(row[11])

            # Десериализация функциональных триграмм
            func_w_trigrams_freqs = json.loads(row[12])
            func_w_trigram_with_pos_counts = json.loads(row[13])

            # Десериализация позиционных данных
            token_positions_normalized_frequencies = json.loads(row[14])
            token_positions_counts = json.loads(row[15])

            # Акумулирование данных для POS n-грамм
            for key, count in pos_unigrams_counts.items():
                pos_unigrams_counts_total[key] += count
            for key, freq in pos_unigrams_freq.items():
                pos_unigrams_freq_total[key] += freq

            for key, count in pos_bigrams_counts.items():
                pos_bigrams_counts_total[key] += count
            for key, freq in pos_bigrams_freq.items():
                pos_bigrams_freq_total[key] += freq

            for key, count in pos_trigrams_counts.items():
                pos_trigrams_counts_total[key] += count
            for key, freq in pos_trigrams_freq.items():
                pos_trigrams_freq_total[key] += freq

            # Акумулирование данных для char n-грамм
            for key, count in char_unigrams_counts.items():
                char_unigrams_counts_total[key] += count
            for key, freq in char_unigrams_freq.items():
                char_unigrams_freq_total[key] += freq

            for key, count in char_bigrams_counts.items():
                char_bigrams_counts_total[key] += count
            for key, freq in char_bigrams_freq.items():
                char_bigrams_freq_total[key] += freq

            for key, count in char_trigrams_counts.items():
                char_trigrams_counts_total[key] += count
            for key, freq in char_trigrams_freq.items():
                char_trigrams_freq_total[key] += freq

                # Акумулирование данных для функциональных триграмм
            for category, trigrams in func_w_trigrams_freqs.items():
                for trigram, freq in trigrams.items():
                    func_w_trigrams_freqs_total[category][trigram] += freq

            for category, trigrams in func_w_trigram_with_pos_counts.items():
                for trigram, count in trigrams.items():
                    func_w_trigram_with_pos_counts_total[category][trigram] += count

            # Акумулирование данных для позиционных токенов
            for position, tokens in token_positions_normalized_frequencies.items():
                for token, freq in tokens.items():
                    token_positions_normalized_frequencies_total[position][token] += freq

            for position, tokens in token_positions_counts.items():
                for token, count in tokens.items():
                    token_positions_counts_total[position][token] += count

        def create_table(counts_dict, freq_dict, min_count):
            table = Table()
            table.add_column("N-gram", style="bold", justify="center", max_width=40)
            table.add_column("Количество", justify="center")
            table.add_column("Частота", justify="center")

            sorted_ngrams = []
            for key in counts_dict:
                total_count = counts_dict[key]
                average_count = total_count / num_texts
                if average_count >= min_count:
                    total_freq = freq_dict.get(key, 0)
                    average_freq = total_freq / num_texts
                    sorted_ngrams.append((key, average_count, average_freq))

            sorted_ngrams.sort(key=lambda x: (-x[2], -x[1]))

            for ngram, avg_count, avg_freq in sorted_ngrams:
                table.add_row(ngram, f"{avg_count:.3f}", f"{avg_freq:.3f}")

            return table

        min_count = min_count_choice()
        print(
            Fore.LIGHTYELLOW_EX + Style.BRIGHT + "\nСРЕДНИЕ ПОКАЗАТЕЛИ ДЛЯ" + Fore.LIGHTGREEN_EX + Style.BRIGHT
            + " UNIGRAMS" + Fore.LIGHTYELLOW_EX + Style.BRIGHT + " В КОРПУСЕ" + Fore.RESET)
        wait_for_enter_to_analyze()
        pos_unigram_table = create_table(pos_unigrams_counts_total, pos_unigrams_freq_total, min_count)
        console.print(pos_unigram_table)
        wait_for_enter_to_analyze()

        print(
            Fore.LIGHTYELLOW_EX + Style.BRIGHT + "СРЕДНИЕ ПОКАЗАТЕЛИ ДЛЯ" + Fore.LIGHTGREEN_EX + Style.BRIGHT
            + " BIGRAMS" + Fore.LIGHTYELLOW_EX + Style.BRIGHT + " В КОРПУСЕ" + Fore.RESET)
        wait_for_enter_to_analyze()
        pos_bigram_table = create_table(pos_bigrams_counts_total, pos_bigrams_freq_total, min_count)
        console.print(pos_bigram_table)
        wait_for_enter_to_analyze()

        print(
            Fore.LIGHTYELLOW_EX + Style.BRIGHT + "СРЕДНИЕ ПОКАЗАТЕЛИ ДЛЯ" + Fore.LIGHTGREEN_EX + Style.BRIGHT
            + " TRIGRAMS" + Fore.LIGHTYELLOW_EX + Style.BRIGHT + " В КОРПУСЕ" + Fore.RESET)
        wait_for_enter_to_analyze()
        pos_trigram_table = create_table(pos_trigrams_counts_total, pos_trigrams_freq_total, min_count)
        console.print(pos_trigram_table)
        wait_for_enter_to_analyze()

        print(
            Fore.LIGHTYELLOW_EX + Style.BRIGHT + "\n            ДАЛЕЕ БУДЕТ ПОКАЗАН АНАЛИЗ БУКВЕННЫХ N-ГРАММОВ" + Fore.RESET)
        print(
            Fore.LIGHTRED_EX + Style.BRIGHT + "Внимание! N-граммы '<' и '>' используются для обозначания начала и конца "
                                      "\nслов соответственно.\n" + Fore.RESET)
        wait_for_enter_to_analyze()
        min_count = min_count_choice()

        print(
            Fore.LIGHTYELLOW_EX + Style.BRIGHT + "\nСРЕДНИЕ ПОКАЗАТЕЛИ ДЛЯ" + Fore.LIGHTGREEN_EX + Style.BRIGHT +
            " UNIGRAMS" + Fore.LIGHTYELLOW_EX + Style.BRIGHT + " В КОРПУСЕ" + Fore.RESET)
        wait_for_enter_to_analyze()
        char_unigram_table = create_table(char_unigrams_counts_total, char_unigrams_freq_total, min_count)
        console.print(char_unigram_table)
        wait_for_enter_to_analyze()

        print(
            Fore.LIGHTYELLOW_EX + Style.BRIGHT + "СРЕДНИЕ ПОКАЗАТЕЛИ ДЛЯ" + Fore.LIGHTGREEN_EX + Style.BRIGHT +
            " BIGRAMS" + Fore.LIGHTYELLOW_EX + Style.BRIGHT + " В КОРПУСЕ" + Fore.RESET)
        wait_for_enter_to_analyze()
        char_bigram_table = create_table(char_bigrams_counts_total, char_bigrams_freq_total, min_count)
        console.print(char_bigram_table)
        wait_for_enter_to_analyze()

        print(
            Fore.LIGHTYELLOW_EX + Style.BRIGHT + "СРЕДНИЕ ПОКАЗАТЕЛИ ДЛЯ" + Fore.LIGHTGREEN_EX + Style.BRIGHT +
            " TRIGRAMS" + Fore.LIGHTYELLOW_EX + Style.BRIGHT + " В КОРПУСЕ" + Fore.RESET)
        wait_for_enter_to_analyze()
        char_trigram_table = create_table(char_trigrams_counts_total, char_trigrams_freq_total, min_count)
        console.print(char_trigram_table)
        wait_for_enter_to_analyze()

        def min_count_choice_for_posiitions():
            while True:
                try:
                    min_count_input = input(Fore.LIGHTGREEN_EX + Style.BRIGHT +
                                            f"Введите минимальное значение для среднего количества выводимых токенов"
                                            f"\nна той или иной позиции или просто нажмите 'Enter', чтобы продолжить"
                                            f"\n(по умолчанию значение=1): \n").strip()

                    if not min_count_input:
                        min_count = 1
                        break
                    else:
                        min_count = float(min_count_input)
                        break
                except ValueError:
                    print(Fore.LIGHTRED_EX + Style.BRIGHT + "\nОшибка! Введите числовое значение." + Fore.RESET)
            return min_count

        print(
            Fore.LIGHTYELLOW_EX + Style.BRIGHT + f"\nДАЛЕЕ БУДУТ ВЫВЕДЕНЫ СРЕДНИЕ ПОЗИЦИОННЫЕ ПОКАЗАТЕЛИ ТОКЕНОВ В ТЕКСТЕ" + Fore.RESET)
        display_position_explanation()
        min_count = min_count_choice_for_posiitions()
        for position in ['first', 'second', 'antepenultimate', 'penultimate', 'last']:
            print(
                Fore.LIGHTYELLOW_EX + Style.BRIGHT + f"\n* Средние показатели для позиций:" + Fore.LIGHTGREEN_EX + Style.BRIGHT + f" {position.upper()}" + Fore.RESET)
            wait_for_enter_to_analyze()
            token_count_table = create_table(
                token_positions_counts_total[position],
                token_positions_normalized_frequencies_total[position],
                min_count
            )
            console.print(token_count_table)
            wait_for_enter_to_analyze()

        print(
            Fore.LIGHTYELLOW_EX + Style.BRIGHT + "\nДАЛЕЕ БУДЕТ ВЫВЕДЕНЫ СРЕДНИЕ ПОКАЗАТЕЛИ ДЛЯ ТРИГРАММОВ С 1,2,3 ФУНКЦИОНАЛЬНЫМИ СЛОВАМИ\n" + Fore.RESET)
        min_count = min_count_choice()
        for category, trigrams in func_w_trigrams_freqs_total.items():
            print(
                Fore.LIGHTYELLOW_EX + Style.BRIGHT + f"\n                  {category.upper()}" + Fore.RESET)
            wait_for_enter_to_analyze()
            trigram_table = create_table(
                func_w_trigram_with_pos_counts_total[category],
                func_w_trigrams_freqs_total[category], min_count
            )
            console.print(trigram_table)
            wait_for_enter_to_choose_opt()

    def delete_text_from_corpus(self, text_id):
        """Удаляет записи о тексте по text_id из всех таблиц."""
        self.cursor.execute("DELETE FROM Text_Passport WHERE text_id = ?", (text_id,))

        self.cursor.execute("DELETE FROM Simplification_features WHERE text_id = ?", (text_id,))

        self.cursor.execute("DELETE FROM Normalisation_features WHERE text_id = ?", (text_id,))

        self.cursor.execute("DELETE FROM Explicitation_features WHERE text_id = ?", (text_id,))

        self.cursor.execute("DELETE FROM Interference_features WHERE text_id = ?", (text_id,))

        self.cursor.execute("DELETE FROM Miscellaneous_features WHERE text_id = ?", (text_id,))

        self.cursor.execute("DELETE FROM Morphological_annotation WHERE text_id = ?", (text_id,))

        self.cursor.execute("DELETE FROM Syntactic_annotation WHERE text_id = ?", (text_id,))

        self.connection.commit()

        print(Fore.LIGHTGREEN_EX + Style.BRIGHT + f"Запись о тексте выбранном тексте и все связанные с ним данные были успешно удалены!\n" + Fore.RESET)