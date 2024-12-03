# -*- coding: utf-8 -*- # Языковая кодировка UTF-8
import nltk

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

try:
    nltk.data.find('tokenizers/punkt_tab/russian')
except LookupError:
    nltk.download('punkt_tab')

import json
import os
import re

from natasha import (Segmenter, MorphVocab, NewsEmbedding,
                     NewsMorphTagger, NewsSyntaxParser, Doc)
import pymorphy2
from colorama import Fore, Style, init
from rich.console import Console
from rich.table import Table

from tools.core import preprocess_text
from tools.core.constants import (NON_TRANSLATED_DB_NAME,
                                  MACHINE_TRANSLATED_DB_NAME,
                                  HUMAN_TRANSLATED_DB_NAME, RETURN_TO_MENU)
from tools.core.tokens_counter import count_tokens
from tools.core.custom_punkt_tokenizer import sent_tokenize_with_abbr
from tools.work_with_db import SaveToDatabase
from tools.core.utils import (wait_for_enter_to_analyze,
                              display_morphological_annotation,
                              format_morphological_features,
                              wait_for_enter_to_choose_opt,
                              check_db_exists, choose_db)
from tools.core.validators import validate_gender, validate_years

from tools.core.data.pronouns import (pers_possessive_pronouns_analysis_list,
                                      reflexive_pronoun_list,
                                      demonstrative_pronouns_list,
                                      defining_pronouns_list,
                                      relative_pronouns_list,
                                      indefinite_pronouns_list,
                                      negative_pronouns_list)

# Импорты для "Simplification_features"
from tools.simplification.lexical_density import calculate_lexical_density
from tools.simplification.lexical_variety import lexical_variety
from tools.simplification.mean_word_length import (mean_word_length_char,
                                                   calculate_syllable_ratio)
from tools.simplification.mean_sent_length import (mean_sentence_length_in_tokens,
                                                   mean_sentence_length_in_chars)
from tools.simplification.mean_word_rank import calculate_mean_word_rank
from tools.simplification.most_frequent_words import (find_n_most_frequent_words,
                                                      count_types_in_text)

# Импорты для "Normalisation_features"
from tools.normalisation.repetition import calculate_repetition

# Импорты для "Explicitation_features"
from tools.explicitation.explicit_naming import calculate_explicit_naming_ratio
from tools.explicitation.single_naming import single_naming_frequency
from tools.explicitation.mean_multiple_naming import calculate_mean_multiple_naming
from tools.explicitation.named_entities_extraction import extract_entities
from tools.explicitation.sci_dm_analysis import sci_dm_search

# Импорты для "Interference_features"
from tools.interference.n_grams_analyzer import pos_ngrams, character_ngrams
from tools.interference.positional_token_freq import calculate_position_frequencies
from tools.interference.positional_tokens_contexts_by_sent import (extract_positions,
                                                                   print_positions)
from tools.interference.contextual_func_words import contextual_function_words_in_trigrams

# Импорты для "Miscellaneous_features"
from tools.miscellaneous.func_words_freqs import compute_function_word_frequencies
from tools.miscellaneous.pronouns_freq import compute_pronoun_frequencies
from tools.miscellaneous.punct_analysis import analyze_punctuation
from tools.miscellaneous.passive_to_all_verbs_ratio import calculate_passive_verbs_ratio
from tools.miscellaneous.flesh_readability_score import flesh_readability_index_for_rus

init(autoreset=True)
console = Console()


class CorpusText:
    def __init__(self, db=None, text=None):
        self.db = db
        self.text = text
        self.title = ""
        self.subject_area = ""
        self.keywords = ""
        self.publication_year = ""
        self.published_in = ""
        self.authors = ""
        self.author_gender = ""
        self.author_birth_year = ""

        self.morph = pymorphy2.MorphAnalyzer()
        self.segmenter = Segmenter()
        self.morph_vocab = MorphVocab()
        self.embedding = NewsEmbedding()
        self.morph_tagger = NewsMorphTagger(self.embedding)
        self.syntax_parser = NewsSyntaxParser(self.embedding)
        self.morphological_analysis_result = None
        self.syntactic_analysis_result = None

    def show_texts(self):
        """Отображает все тексты с их порядковыми номерами и
         позволяет выбрать один для отображения подробной информации."""
        with SaveToDatabase(self.db) as db_fetch:
            db_fetch.display_texts()

    def analyze_and_save(self, show_analysis=False):
        # Анализ Simplification_features
        if show_analysis:
            print("\n" + Fore.LIGHTWHITE_EX + "*" * 100)
            print(
                Fore.GREEN + Style.BRIGHT +
                "                               ИНДИКАТОРЫ ХАРАКТЕРИСТИКИ"
                + Fore.LIGHTGREEN_EX + Style.BRIGHT + " SIMPLIFICATION")
            print(Fore.LIGHTWHITE_EX + "*" * 100)
            wait_for_enter_to_analyze()
        lexical_density = calculate_lexical_density(self.text, show_analysis)  # OK

        ttr_lex_variety, log_ttr_lex_variety, modified_lex_variety = lexical_variety(self.text, show_analysis)  # OK

        mean_word_length = mean_word_length_char(self.text, show_analysis)  # OK

        syllable_ratio, total_syllables_count = calculate_syllable_ratio(self.text, show_analysis)  # OK

        tokens_mean_sent_length = mean_sentence_length_in_tokens(self.text, show_analysis)  # OK
        chars_mean_sent_length = mean_sentence_length_in_chars(self.text, show_analysis)  # OK
        mean_word_rank_1, mean_word_rank_2, = calculate_mean_word_rank(self.text, show_analysis)  # OK
        most_freq_words = find_n_most_frequent_words(self.text, show_analysis=show_analysis)  # OK
        types_counts = count_types_in_text(self.text)
        all_tokens_count, alpha_tokens_count, all_punct_tokens_count = count_tokens(self.text)

        if show_analysis:
            # Анализ Normalisation_features
            print("\n" + Fore.LIGHTWHITE_EX + "*" * 100)
            print(
                Fore.GREEN + Style.BRIGHT +
                "                               ИНДИКАТОРЫ ХАРАКТЕРИСТИКИ"
                + Fore.LIGHTGREEN_EX + Style.BRIGHT + " NORMALISATION")
            print(Fore.LIGHTWHITE_EX + "*" * 100)
            wait_for_enter_to_analyze()
        repetition, repeated_content_words_count, repeated_content_words, total_word_tokens = calculate_repetition(
            self.text, show_analysis)  # OK

        if show_analysis:
            # Анализ Explicitation_features
            print("\n" + Fore.LIGHTWHITE_EX + "*" * 100)
            print(
                Fore.GREEN + Style.BRIGHT +
                "                               ИНДИКАТОРЫ ХАРАКТЕРИСТИКИ" +
                Fore.LIGHTGREEN_EX + Style.BRIGHT + " EXPLICITATION")
            print(Fore.LIGHTWHITE_EX + "*" * 100)
            wait_for_enter_to_analyze()
        explicit_naming_ratio = calculate_explicit_naming_ratio(self.text, show_analysis)  # OK
        single_naming = single_naming_frequency(self.text, show_analysis)  # OK
        mean_multiple_naming, single_entities, single_entities_count, multiple_entities, multiple_entities_count = calculate_mean_multiple_naming(
            self.text, show_analysis)  # OK
        named_entities, named_entities_count = extract_entities(self.text, show_analysis)  # OK

        (total_tokens_with_dms, sci_markers_total_count, found_sci_dms, markers_counts,
         topic_intro_dm_count, topic_intro_dm_in_ord, topic_intro_dm_freq,
         info_sequence_count, info_sequence_in_ord, info_sequence_freq,
         illustration_dm_count, illustration_dm_in_ord, illustration_dm_freq,
         material_sequence_count, material_sequence_in_ord, material_sequence_freq,
         conclusion_dm_count, conclusion_dm_in_ord, conclusion_dm_freq,
         intro_new_addit_info_count, intro_new_addit_info_in_ord, intro_new_addit_info_freq,
         info_explanation_or_repetition_count, info_explanation_or_repetition_in_ord,
         info_explanation_or_repetition_freq, contrast_dm_count, contrast_dm_in_ord,
         contrast_dm_freq, examples_introduction_dm_count, examples_introduction_dm_in_ord,
         examples_introduction_dm_freq,
         author_opinion_count, author_opinion_in_ord, author_opinion_freq,
         author_attitude_count, author_attitude_in_ord, author_attitude_freq,
         high_certainty_modal_words_count, high_certainty_modal_words_in_ord,
         high_certainty_modal_words_freq,
         moderate_certainty_modal_words_count, moderate_certainty_modal_words_in_ord,
         moderate_certainty_modal_words_freq,
         uncertainty_modal_words_count, uncertainty_modal_words_in_ord, uncertainty_modal_words_freq,
         call_to_action_dm_count, call_to_action_dm_in_ord, call_to_action_dm_freq,
         joint_action_count, joint_action_in_ord, joint_action_freq, putting_emphasis_dm_count,
         putting_emphasis_dm_in_ord, putting_emphasis_dm_freq, refer_to_background_knowledge_count,
         refer_to_background_knowledge_in_ord, refer_to_background_knowledge_freq
         ) = sci_dm_search(self.text, show_analysis)  # OK

        if show_analysis:
            # Анализ Interference_features
            print("\n" + Fore.LIGHTWHITE_EX + "*" * 100)
            print(
                Fore.GREEN + Style.BRIGHT +
                "                               ИНДИКАТОРЫ ХАРАКТЕРИСТИКИ" +
                Fore.LIGHTGREEN_EX + Style.BRIGHT + " INTERFERENCE")
            print(Fore.LIGHTWHITE_EX + "*" * 100)
            wait_for_enter_to_analyze()

        (pos_unigrams_counts, pos_unigrams_freq, pos_bigrams_counts,
         pos_bigrams_freq, pos_trigrams_counts, pos_trigrams_freq) = pos_ngrams(self.text,
                                                                                show_analysis=show_analysis)  # OK

        (char_unigram_counts, char_unigram_freq, char_bigram_counts,
         char_bigram_freq, char_trigram_counts, char_trigram_freq) = character_ngrams(self.text,
                                                                                      show_analysis=show_analysis)  # OK

        token_positions_normalized_frequencies, token_positions_counts = calculate_position_frequencies(self.text,
                                                                                                        show_analysis)  # OK

        token_positions_in_sent = extract_positions(self.text, show_analysis=False)  # OK
        if show_analysis:
            print(
                Fore.GREEN + Style.BRIGHT +
                "\n             ТОКЕНЫ И ИХ ЧАСТИ РЕЧИ НА РАЗНЫХ ПОЗИЦИЯХ В ПРЕДЛОЖЕНИИ"
                + Fore.RESET)
            print(
                Fore.LIGHTGREEN_EX + Style.BRIGHT +
                "* Выводятся контексты предложений, длиннее 5 токенов." + Fore.RESET)
            wait_for_enter_to_analyze()
            print_positions(token_positions_in_sent)

        func_w_trigrams_freqs, func_w_trigram_with_pos_counts, func_w_full_contexts = contextual_function_words_in_trigrams(
            self.text, show_analysis)

        if show_analysis:
            # Анализ Miscellaneous_features
            print("\n" + Fore.LIGHTWHITE_EX + "*" * 100)

            print(
                Fore.GREEN + Style.BRIGHT +
                "                                     ОСТАЛЬНЫЕ" +
                Fore.LIGHTGREEN_EX + Style.BRIGHT + " ИНДИКАТОРЫ")
            print(Fore.LIGHTWHITE_EX + "*" * 100)
            wait_for_enter_to_analyze()

        func_words_freq, func_words_counts = compute_function_word_frequencies(self.text, show_analysis)  # OK
        pers_possessive_pronouns_frequencies, pers_possessive_pronouns_counts = compute_pronoun_frequencies(self.text,
                                                                                                            pers_possessive_pronouns_analysis_list,
                                                                                                            show_analysis)
        reflexive_pronoun_frequencies, reflexive_pronoun_counts = compute_pronoun_frequencies(self.text,
                                                                                              reflexive_pronoun_list,
                                                                                              show_analysis)
        demonstrative_pronouns_frequencies, demonstrative_pronouns_counts = compute_pronoun_frequencies(self.text,
                                                                                                        demonstrative_pronouns_list,
                                                                                                        show_analysis)
        defining_pronouns_frequencies, defining_pronouns_counts = compute_pronoun_frequencies(self.text,
                                                                                              defining_pronouns_list,
                                                                                              show_analysis)
        relative_pronouns_frequencies, relative_pronouns_counts = compute_pronoun_frequencies(self.text,
                                                                                              relative_pronouns_list,
                                                                                              show_analysis)
        indefinite_pronouns_frequencies, indefinite_pronouns_counts = compute_pronoun_frequencies(self.text,
                                                                                                  indefinite_pronouns_list,
                                                                                                  show_analysis)
        negative_pronouns_frequencies, negative_pronouns_counts = compute_pronoun_frequencies(self.text,
                                                                                              negative_pronouns_list,
                                                                                              show_analysis)

        punct_marks_normalized_frequency, punct_marks_to_all_punct_frequency, punctuation_counts = analyze_punctuation(
            self.text,
            show_analysis)

        passive_to_all_v_ratio, passive_verbs, passive_verbs_count, all_verbs, all_verbs_count = calculate_passive_verbs_ratio(
            self.text, show_analysis)

        readability_index = flesh_readability_index_for_rus(self.text, show_analysis)

        # Использование контекстного менеджера для работы с базой данных
        with SaveToDatabase(self.db) as db_saver:
            db_saver.insert_simplification_features(
                lexical_density, ttr_lex_variety,
                log_ttr_lex_variety, modified_lex_variety, mean_word_length,
                syllable_ratio, total_syllables_count, tokens_mean_sent_length,
                chars_mean_sent_length, mean_word_rank_1, mean_word_rank_2,
                most_freq_words, types_counts, all_tokens_count, alpha_tokens_count, all_punct_tokens_count
            )

            db_saver.insert_normalisation_features(
                repetition, repeated_content_words_count,
                repeated_content_words, total_word_tokens
            )

            db_saver.insert_explicitation_features(
                explicit_naming_ratio, single_naming, mean_multiple_naming, single_entities, single_entities_count,
                multiple_entities, multiple_entities_count,
                named_entities, named_entities_count,
                total_tokens_with_dms, sci_markers_total_count, found_sci_dms, markers_counts,
                topic_intro_dm_count, topic_intro_dm_in_ord, topic_intro_dm_freq,
                info_sequence_count, info_sequence_in_ord, info_sequence_freq,
                illustration_dm_count, illustration_dm_in_ord, illustration_dm_freq,
                material_sequence_count, material_sequence_in_ord, material_sequence_freq,
                conclusion_dm_count, conclusion_dm_in_ord, conclusion_dm_freq,
                intro_new_addit_info_count, intro_new_addit_info_in_ord, intro_new_addit_info_freq,
                info_explanation_or_repetition_count, info_explanation_or_repetition_in_ord,
                info_explanation_or_repetition_freq, contrast_dm_count, contrast_dm_in_ord,
                contrast_dm_freq, examples_introduction_dm_count, examples_introduction_dm_in_ord,
                examples_introduction_dm_freq, author_opinion_count, author_opinion_in_ord,
                author_opinion_freq,
                author_attitude_count, author_attitude_in_ord, author_attitude_freq,
                high_certainty_modal_words_count, high_certainty_modal_words_in_ord,
                high_certainty_modal_words_freq,
                moderate_certainty_modal_words_count, moderate_certainty_modal_words_in_ord,
                moderate_certainty_modal_words_freq,
                uncertainty_modal_words_count, uncertainty_modal_words_in_ord, uncertainty_modal_words_freq,
                call_to_action_dm_count, call_to_action_dm_in_ord, call_to_action_dm_freq,
                joint_action_count, joint_action_in_ord, joint_action_freq, putting_emphasis_dm_count,
                putting_emphasis_dm_in_ord, putting_emphasis_dm_freq, refer_to_background_knowledge_count,
                refer_to_background_knowledge_in_ord, refer_to_background_knowledge_freq,
            )

            db_saver.insert_interference_features(
                pos_unigrams_counts, pos_unigrams_freq, pos_bigrams_counts,
                pos_bigrams_freq, pos_trigrams_counts, pos_trigrams_freq,
                char_unigram_counts, char_unigram_freq, char_bigram_counts,
                char_bigram_freq, char_trigram_counts, char_trigram_freq,
                token_positions_normalized_frequencies, token_positions_counts,
                token_positions_in_sent, func_w_trigrams_freqs,
                func_w_trigram_with_pos_counts, func_w_full_contexts
            )
            db_saver.insert_miscellaneous_features(
                func_words_freq, func_words_counts,
                pers_possessive_pronouns_frequencies, pers_possessive_pronouns_counts,
                reflexive_pronoun_frequencies, reflexive_pronoun_counts,
                demonstrative_pronouns_frequencies, demonstrative_pronouns_counts,
                defining_pronouns_frequencies, defining_pronouns_counts,
                relative_pronouns_frequencies, relative_pronouns_counts,
                indefinite_pronouns_frequencies, indefinite_pronouns_counts,
                negative_pronouns_frequencies, negative_pronouns_counts,
                punct_marks_normalized_frequency,
                punct_marks_to_all_punct_frequency, punctuation_counts,
                passive_to_all_v_ratio, passive_verbs, passive_verbs_count,
                all_verbs, all_verbs_count, readability_index
            )

    def save_text_passport(self, text, title, subject_area, keywords,
                           publication_year, published_in,
                           authors, author_gender, author_birth_year):
        # Использование контекстного менеджера для работы с базой данных
        with SaveToDatabase(self.db) as db_saver:
            db_saver.insert_text_passport(
                text, title, subject_area, keywords, publication_year, published_in,
                authors, author_gender, author_birth_year
            )

    def create_text_passport(self):
        """Метод для ввода информации о паспорте текста и установки соответствующих атрибутов."""
        print(Fore.GREEN + Style.BRIGHT + "\nСОЗДАНИЕ ПАСПОРТА ТЕКСТА")
        self.text = self.text
        # Обязательные поля
        self.title = input("Введите название статьи (обязательно): ").strip()
        while not self.title:
            self.title = input(Fore.LIGHTRED_EX + "Название статьи не может быть пустым. "
                                                  "\nВведите название статьи: " + Fore.RESET).strip()

        self.subject_area = input("Введите предметную область (обязательно): ").strip()
        while not self.subject_area:
            self.subject_area = input(Fore.LIGHTRED_EX + "Предметная область не может быть пустой. "
                                                         "\nВведите предметную область: " + Fore.RESET).strip()
        # Необязательные поля
        self.keywords = input("Введите указанные в статье ключевые слова (через запятую): ").strip()
        while True:
            try:
                self.publication_year = input("Введите год публикации: ").strip()
                if self.publication_year:
                    self.publication_year = validate_years(self.publication_year, "года публикации",
                                                           single_year=True)
                break
            except ValueError as e:
                print(Fore.LIGHTRED_EX + str(e) + Fore.RESET)
        self.published_in = input("Введите место публикации (журнал): ")

        self.authors = input("Введите имена автора(ов) статьи: ")
        self.author_gender = validate_gender(input("Введите пол автора(ов) (м/ж через запятую): ").strip())
        while True:
            try:
                self.author_birth_year = input("Введите год(ы) рождения автора(ов) (через запятую): ").strip()
                if self.author_birth_year:
                    self.author_birth_year = validate_years(self.author_birth_year, "год(ы) рождения")
                break
            except ValueError as e:
                print(Fore.LIGHTRED_EX + str(e) + Fore.RESET)

        print(Fore.LIGHTGREEN_EX + Style.BRIGHT + "\nПАСПОРТ ТЕКСТА УСПЕШНО СОЗДАН!")

    def display_text_passport(self):
        """Метод для отображения паспорта текста в виде таблицы."""
        print(Fore.GREEN + Style.BRIGHT + "\n                      ПАСПОРТ ТЕКСТА")
        table = Table()
        table.add_column("Поле", style="bold", min_width=20)
        table.add_column("Значение")

        table.add_row("Название статьи", self.title)
        table.add_row("Предметная область", self.subject_area)

        if self.keywords:
            table.add_row("Ключевые слова", self.keywords)
        if self.publication_year:
            table.add_row("Год публикации", str(self.publication_year))
        if self.published_in:
            table.add_row("Место публикации (журнал)", self.published_in)
        if self.authors:
            table.add_row("Автор(ы)", self.authors)
        if self.author_gender:
            table.add_row("Пол автора(ов)", self.author_gender)
        if self.author_birth_year:
            table.add_row("Год рождения автора(ов)", self.author_birth_year)

        console.print(table)

    def fix_spacing(self):
        """Удаляет лишние пробелы и исправляет пунктуацию."""
        text = self.text
        # Удаление символов новой строки и замена их на один пробел
        text = re.sub(r'\n+', ' ', text)
        # Регулярное выражение для поиска шаблона "Заглавная буква. Заглавная буква"
        pattern = r'([А-Яа-яЁё])\.([А-Яа-яЁё])'
        # Замена на "Заглавная буква . Пробел Заглавная буква"
        text = re.sub(pattern, r'\1. \2', text)
        # Замена любых последовательностей пробелов (больше одного) на один пробел
        text = re.sub(r'\s+', ' ', text)
        # Обработка знаков препинания, сливающихся со словом
        text = re.sub(r'([,.!?])([А-Яа-яЁё])', r'\1 \2', text)
        # Удаление лишних пробелов перед знаками препинания
        text = re.sub(r'\s+([,.!?])', r'\1', text)
        self.text = text
        return text

    def get_morphological_annotation(self):
        """Метод для выполнения морфологической разметки текста."""
        sentences = sent_tokenize_with_abbr(self.text)
        all_sentences_info = []
        for sentence in sentences:
            tokens_morph_info = {}
            text = re.sub(r'([\.\,\!\"\„\”\«\»\‘\’\(\)\?\;\%\)\)\[\]\:\—])', r' \1 ', sentence)
            punctuation = set(".,!?;%)([]—")
            token_index = 1

            for token in text.split():
                token = token.strip()
                if re.match(r'\d+', token):
                    pos = 'NUMBER'
                    lemma = token
                    morph_features = 'N/A'
                elif token in punctuation:
                    pos = 'PUNCT'
                    lemma = token
                    morph_features = 'N/A'
                elif re.match(r'[a-zA-Z]', token):
                    pos = 'LATN'
                    lemma = token.lower()
                    morph_features = 'N/A'
                else:
                    parsed_token = self.morph.parse(token)[0]  # Берем наиболее вероятный разбор
                    pos = parsed_token.tag.POS if parsed_token.tag.POS else 'UNKNOWN'
                    lemma = parsed_token.normal_form
                    morph_features = format_morphological_features(parsed_token.tag)

                tokens_morph_info[f'Token {token_index}'] = {
                    "token": token,
                    "lemma": lemma,
                    "POS": pos,
                    "morph_features": morph_features
                }

                token_index += 1

            all_sentences_info.append(tokens_morph_info)

        self.morphological_analysis_result = all_sentences_info
        morph_analysis_str = json.dumps(all_sentences_info, ensure_ascii=False, indent=4)

        with SaveToDatabase(self.db) as db_saver:
            db_saver.insert_morphological_annotation(
                morph_analysis_str
            )
        return all_sentences_info

    def get_syntactic_annotation(self, save=True):
        """Метод для выполнения синтаксической разметки текста с использованием Natasha."""
        self.syntactic_analysis_result = []

        doc = Doc(self.text)

        # Сегментация на предложения для дальнейшего анализа
        doc.segment(self.segmenter)
        # Морфологический анализ для дальнейшего синтаксического анализа
        doc.tag_morph(self.morph_tagger)
        # Анализ синтаксиса
        doc.parse_syntax(self.syntax_parser)
        # Сохраняем результат анализа
        self.syntactic_analysis_result = doc

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

        # Преобразуем список словарей в строку в формате JSON
        synt_analysis_string = json.dumps(tokens_info, ensure_ascii=False, indent=4)
        if save:
            with SaveToDatabase(self.db) as db_saver:
                db_saver.insert_syntactic_annotation(
                    synt_analysis_string
                )
        return synt_analysis_string

    def display_syntactic_annotation(self):
        """Метод для отображения синтаксической разметки в виде древовидной структуры, аналогичной Natasha."""
        if self.syntactic_analysis_result:
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
            total_sentences = len(self.syntactic_analysis_result.sents)
            start = 0
            batch_size = 5

            while start < total_sentences:
                end = min(start + batch_size, total_sentences)

                for i in range(start, end):
                    print(Fore.GREEN + Style.BRIGHT + f'\nПРЕДЛОЖЕНИЕ {i + 1}:\n' + Fore.RESET)
                    self.syntactic_analysis_result.sents[i].syntax.print()
                    print("\n" + Fore.LIGHTBLUE_EX + Style.BRIGHT + "*" * 150)

                start = end  # Обновляем значение start до фактического конца отображенных предложений
                print(
                    Fore.LIGHTWHITE_EX + Style.BRIGHT + f"Отображено {start} предложений. Всего предложений:"
                                                        f" {total_sentences}" + Fore.RESET)

                if start < total_sentences:
                    user_input = input(
                        Fore.LIGHTGREEN_EX + Style.BRIGHT + "Отобразить следующие 5 предложений (y/n)?"
                                                             " \n" + Fore.RESET).strip().lower()

                    while user_input not in ['y', 'n']:
                        user_input = input(
                            Fore.LIGHTRED_EX + "Неверный ввод. Пожалуйста, выберите один из возможных вариантов (y/n):"
                                               " \n" + Fore.RESET).strip().lower()

                    if user_input == 'n':
                        break
        else:
            print("Синтаксический анализ еще не был выполнен.")

    def run_analysis_pipeline(self):
        """Запуск анализа текста."""
        self.create_text_passport()
        self.display_text_passport()
        self.fix_spacing()

        while True:
            print(Fore.LIGHTGREEN_EX + Style.BRIGHT + "\nОтобразить анализ текста в консоль (y/n)?")
            user_display_choice = input()
            if user_display_choice.lower() == 'y':
                show_analysis = True
                break
            elif user_display_choice.lower() == 'n':
                print(Fore.GREEN + Style.BRIGHT + "\nПОЖАЛУЙСТА, ДОЖДИТЕСЬ ОКОНЧАНИЯ АНАЛИЗА.")
                show_analysis = False
                break
            else:
                print(
                    Fore.LIGHTRED_EX + "Неверный ввод. Пожалуйста, выберите один из возможных вариантов (y/n)." + Fore.RESET)
                continue

        self.analyze_and_save(show_analysis)
        print(
            Fore.GREEN + Style.BRIGHT + "\nАНАЛИЗ ИНДИКАТОРОВ ФЕНОМЕНА" + Fore.LIGHTGREEN_EX + Style.BRIGHT +
            " TRANSLATIONESE " + Fore.GREEN + Style.BRIGHT + "УСПЕШНО ЗАВЕРШЕН!")
        print(Fore.LIGHTGREEN_EX + Style.BRIGHT + "РЕЗУЛЬТАТЫ АНАЛИЗА СОХРАНЕНЫ В БАЗУ ДАННЫХ.\n" + Fore.RESET)
        wait_for_enter_to_analyze()
        self.save_text_passport(
            self.text, self.title, self.subject_area, self.keywords, self.publication_year,
            self.published_in, self.authors, self.author_gender, self.author_birth_year)

        morph_ann = self.get_morphological_annotation()
        print(
            Fore.GREEN + Style.BRIGHT + "\nМОРФОЛОГИЧЕСКАЯ РАЗМЕТКА СОЗДАНА И СОХРАНЕНА В БАЗУ ДАННЫХ")
        print(Fore.LIGHTRED_EX + Style.BRIGHT + "Внимание! Разметка может занять много места на экране.")
        while True:
            display_morph_ann = input(
                Fore.LIGHTGREEN_EX + Style.BRIGHT + "\nОтобразить морфологическую разметку текста (y/n)?\n")
            if display_morph_ann.lower() == 'y':
                display_morphological_annotation(morph_ann)
                break
            elif display_morph_ann.lower() == 'n':
                break
            else:
                print(Fore.LIGHTRED_EX + "Неверный ввод. Пожалуйста, выберите один из возможных вариантов (y/n).")
                continue
        self.get_syntactic_annotation()

        print(Fore.GREEN + Style.BRIGHT + "\nСИНТАКСИЧЕСКАЯ РАЗМЕТКА СОЗДАНА И СОХРАНЕНА В БАЗУ ДАННЫХ.")
        print(Fore.LIGHTRED_EX + Style.BRIGHT + "Внимание! Разметка может занять много места на экране.")
        while True:
            display_synt_ann = input(
                Fore.LIGHTGREEN_EX + Style.BRIGHT + "\nОтобразить синтаксическую разметку текста (y/n)?\n")
            if display_synt_ann.lower() == 'y':
                self.display_syntactic_annotation()
                break
            elif display_synt_ann.lower() == 'n':
                break
            else:
                print(Fore.LIGHTRED_EX + "Неверный ввод. Пожалуйста, выберите один из возможных вариантов (y/n).")
                continue

    def display_corpus_info(self, choice=None):
        """
        Отображает общую информацию о корпусе текстов
        """
        if not choice:
            with SaveToDatabase(self.db) as db_corpus_info:
                db_corpus_info.display_corpus_info()
        else:
            with SaveToDatabase() as db_corpora_comparison:
                db_corpora_comparison.display_corpus_info(choice)


def user_interface():
    print(
        Fore.GREEN + Style.BRIGHT + '\nАНАЛИЗАТОР ФЕНОМЕНА' + Fore.LIGHTGREEN_EX + Style.BRIGHT + ' TRANSLATIONESE' + Fore.GREEN + Style.BRIGHT + ' ЗАПУЩЕН\n' + Fore.RESET)
    while True:
        print(Fore.GREEN + Style.BRIGHT + "Выберите действие: ")
        print(Fore.GREEN + Style.BRIGHT + "1." + Style.NORMAL + Fore.BLACK + " Проанализировать новый текст")
        print(
            Fore.GREEN + Style.BRIGHT + "2." + Style.NORMAL + Fore.BLACK + " Отобразить информацию о выбранном тексте в корпусе")
        print(
            Fore.GREEN + Style.BRIGHT + "3." + Style.NORMAL + Fore.BLACK + " Отобразить информацию о выбранном корпусе")
        print(
            Fore.GREEN + Style.BRIGHT + "4." + Style.NORMAL + Fore.BLACK + " Отобразить средние показатели по всем корпусам")
        print(
            Fore.GREEN + Style.BRIGHT + "5." + Style.NORMAL + Fore.BLACK + " Подготовить текст к анализу (удаление ссылок, выравнивание текста по длине)")
        print(Fore.LIGHTBLACK_EX + Style.BRIGHT + "6." + Style.NORMAL + Fore.LIGHTBLACK_EX + " Выйти из программы")

        choice = input(Fore.GREEN + Style.BRIGHT + "Введите номер действия: \n")

        if choice == "1":
            db = choose_db()
            if not db:
                print(Fore.LIGHTRED_EX + Style.BRIGHT + RETURN_TO_MENU)
                continue

            text_to_analyse = text_input_for_analysis()
            print(Fore.LIGHTGREEN_EX + Style.BRIGHT + f"\nТекст будет сохранен в базу данных: {db}.")
            corpus_text = CorpusText(text=text_to_analyse, db=db)
            corpus_text.run_analysis_pipeline()
            wait_for_enter_to_choose_opt()

        elif choice == "2":
            db = choose_db()
            if not db:
                print(Fore.LIGHTRED_EX + Style.BRIGHT + RETURN_TO_MENU)
                continue
            corpus = CorpusText(db=db)
            corpus.show_texts()

        elif choice == "3":
            db = choose_db()
            if not db:
                print(Fore.LIGHTRED_EX + Style.BRIGHT + RETURN_TO_MENU)
                continue
            corpus = CorpusText(db=db)
            corpus.display_corpus_info()
        elif choice == "4":
            corpus = CorpusText()
            if (
                    check_db_exists(NON_TRANSLATED_DB_NAME)
                    and check_db_exists(MACHINE_TRANSLATED_DB_NAME)
                    and check_db_exists(HUMAN_TRANSLATED_DB_NAME)
            ):
                corpus.display_corpus_info(choice='all')

            elif (
                    check_db_exists(NON_TRANSLATED_DB_NAME)
                    and check_db_exists(MACHINE_TRANSLATED_DB_NAME)
            ):
                corpus.display_corpus_info(choice='auth_mt')
            elif (
                    check_db_exists(NON_TRANSLATED_DB_NAME)
                    and check_db_exists(HUMAN_TRANSLATED_DB_NAME)
            ):
                corpus.display_corpus_info(choice='auth_ht')
            elif (
                    check_db_exists(MACHINE_TRANSLATED_DB_NAME)
                    and check_db_exists(HUMAN_TRANSLATED_DB_NAME)
            ):
                corpus.display_corpus_info(choice='mt_ht')

            else:
                print(Fore.LIGHTRED_EX + Style.BRIGHT + "Для сравнение необходимо наличие хотя бы двух корпусов.")

        elif choice == "5":
            preprocess_text.main()
        elif choice == "6":
            print(Fore.LIGHTRED_EX + Style.BRIGHT + "\nВыход из программы.")
            exit()
        else:
            print(Fore.LIGHTRED_EX + Style.BRIGHT + "Неверный выбор. Пожалуйста, попробуйте снова.\n")


def process_text_from_file(file_path):
    """Обрабатывает текст из файла и сохраняет результат."""
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()
    return text


def text_input_for_analysis():
    print("\n" + Fore.LIGHTWHITE_EX + "*" * 100)
    print(
        Fore.GREEN + Style.BRIGHT + "                     ВВОД ТЕКСТА ДЛЯ ПОСЛЕДУЮЩЕГО АНАЛИЗА" + Fore.RESET)
    print(Fore.LIGHTWHITE_EX + "*" * 100)
    print(
        Fore.LIGHTRED_EX + Style.BRIGHT + "Внимание! Текст должен быть заранее предобработан и готов для "
                                          "последующего анализа." + Fore.RESET)

    while True:
        mode = input(
            Fore.GREEN + Style.BRIGHT + "Введите 'f' для обработки файла или 't' для ввода текста вручную: \n" + Fore.RESET).strip().lower()
        if mode.lower().strip() == 'f':
            while True:
                print(
                    Fore.GREEN + Style.BRIGHT + "\nВыберите директорию с Вашим текстовым файлом (.txt)." + Fore.RESET)
                print(Fore.BLACK + "1. Директория с аутентичными текстами /auth_ready/")
                print(Fore.BLACK + "2. Директория с машинными переводами /mt_ready/")
                print(Fore.BLACK + "3. Директория с переводами, сделанными человеком /ht_ready/")
                dir_choice = input(
                    Fore.GREEN + Style.BRIGHT + "Введите номер директории: " + Fore.RESET).strip()

                if dir_choice == '1':
                    directory = "auth_ready/"
                elif dir_choice == '2':
                    directory = "mt_ready/"
                elif dir_choice == '3':
                    directory = "ht_ready/"
                else:
                    print(Fore.LIGHTRED_EX + Style.BRIGHT + "\nНеверный выбор. Попробуйте снова." + Fore.RESET)
                    continue

                file_name = input(Fore.GREEN + "Введите название файла в"
                                                        " выбранной директории "
                                                        "(только файлы .txt): " + Fore.RESET).strip()
                file_path = directory + file_name + '.txt'
                if os.path.isfile(file_path):

                    return process_text_from_file(file_path)
                else:
                    print(
                        Fore.LIGHTRED_EX + Style.BRIGHT + "Файл не найден. Проверьте путь и попробуйте снова." + Fore.RESET)
                continue
        elif mode.lower().strip() == 't':
            print(Fore.GREEN + Style.BRIGHT + "\nВведите текст для анализа (по окончанию ввода"
                                                      " напечатайте 'r' с красной строки и нажмите 'Enter').")
            print(
                Fore.RED + Style.BRIGHT + "Для возврата в главное меню напечатайте 'x' с красной строки и нажмите 'Enter'.")
            text_lines = []
            while True:
                line = input()
                if line.lower().strip() == "r":
                    break
                elif line.lower().strip() == "x":
                    print(Fore.LIGHTRED_EX + Style.BRIGHT + "Возвращение в главное меню.\n")
                    break
                text_lines.append(line)

            if line.lower() == "x":
                continue

            input_text = '\n'.join(text_lines).strip()
            if not input_text:
                print(Fore.LIGHTRED_EX + Style.BRIGHT + "Текст не был введен. Попробуйте снова.\n")
                continue
            return input_text


user_interface()
