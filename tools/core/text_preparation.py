# -*- coding: utf-8 -*- # Языковая кодировка UTF-8
import re
import sys

from tools.core.data.abbreviations import abbreviations_with_point


class TextPreProcessor:
    def __init__(self):
        self.abbreviations = abbreviations_with_point

    def fix_spacing(self, text):
        """Исправляет пробелы и форматирование в тексте.

         Заменяет символы новой строки на пробелы, корректирует пробелы перед и после точек и тире, а также удаляет
         лишние пробелы и тире, окруженные пробелами.

         :param text: Исходный текст для обработки.
         :return: Текст с исправленными пробелами и форматированием.
         """
        # Удаление символов новой строки и замена их на один пробел
        text = re.sub(r'\n+', ' ', text)
        # Регулярное выражение для поиска шаблона "Заглавная буква.Заглавная буква"
        pattern_1 = r'([А-Яа-яЁё])\.([А-Яа-яЁё])'
        # Замена на "Заглавная буква . Пробел Заглавная буква"
        text = re.sub(pattern_1, r'\1. \2', text)
        # Регулярное выражение для поиска шаблона "Заглавная/маленькая буква.маленькая буква"
        pattern_2 = r'([А-Яа-яЁё])\.([а-яё])'
        # Замена на "Заглавная буква . Пробел Заглавная буква"
        text = re.sub(pattern_2, r'\1. \2', text)
        # Замена любых последовательностей пробелов (больше одного) на один пробел
        text = re.sub(r'\s+', ' ', text)
        # Удаление "-" если он окружен пробелами
        text = re.sub(r' - ', ' ', text)

        # Удаление "-" перед словом
        text = re.sub(r' -(\w)', r' \1', text)
        return text

    def fix_spacing_for_mean_sent_len(self, text):
        """Исправляет пробелы в тексте для вычисления средней длины предложений.

        Заменяет символы новой строки на пробелы, корректирует пробелы перед и после точек, а также удаляет лишние
        пробелы и тире, окруженные пробелами.

        :param text: Исходный текст для обработки.
        :return: Текст с исправленными пробелами.
        """
        # Удаление символов новой строки и замена их на один пробел
        text = re.sub(r'\n+', ' ', text)
        # Регулярное выражение для поиска шаблона "Заглавная буква.Заглавная буква"
        pattern_1 = r'([А-Яа-яЁё])\.([А-Яа-яЁё])'
        # Замена на "Заглавная буква . Пробел Заглавная буква"
        text = re.sub(pattern_1, r'\1. \2', text)
        # Регулярное выражение для поиска шаблона "Заглавная/маленькая буква.маленькая буква"
        pattern_2 = r'([А-Яа-яЁё])\.([а-яё])'
        # Замена на "Заглавная буква . Пробел Заглавная буква"
        text = re.sub(pattern_2, r'\1. \2', text)
        # Замена любых последовательностей пробелов (больше одного) на один пробел
        text = re.sub(r'\s+', ' ', text)

        # Удаление "-" перед словом
        text = re.sub(r' -(\w)', r' \1', text)
        return text
    def point_abbr_to_full(self, text):
        """Заменяет аббревиатуры на полные формы в тексте.

        Использует отсортированный список аббревиатур для замены их полными формами в тексте.

        :param text: Исходный текст с аббревиатурами.
        :return: Текст с замененными аббревиатурами на полные формы.
        """
        abbreviation_items = list(self.abbreviations.items())  # Получаем список кортежей
        abbreviation_items.sort(key=lambda x: len(x[0]), reverse=True)

        # Применение замен в тексте
        for abbreviation, full_form in abbreviation_items:
            pattern = r'\b' + re.escape(abbreviation)
            text = re.sub(pattern, full_form, text)
        return text

    def process_text(self, text):
        """Обрабатывает текст, заменяя аббревиатуры и исправляя пробелы.

        Сначала заменяет аббревиатуры на полные формы, затем исправляет пробелы и форматирование.

        :param text: Исходный текст для обработки.
        :return: Обработанный текст.
        """
        text = self.point_abbr_to_full(text)
        text = self.fix_spacing(text)
        return text


def get_full_input():
    print("Введите текст для анализа (нажмите Command+D для завершения ввода):")
    input_text = sys.stdin.read()
    return input_text


# Использование класса
if __name__ == "__main__":
    processor = TextPreProcessor()

    # Текст для примера (сгенерирован ИИ)
    text = """
    Осенний ветер за окном напоминал о скором приходе холодов. Листья деревьев медленно кружились в воздухе, постепенно 
    покрывая землю золотым ковром. В парке гуляли немногочисленные прохожие, наслаждаясь последними тёплыми днями. Вдоль 
    аллеи бежала собака, радостно виляя хвостом. Маленький мальчик с интересом наблюдал за ней, крепко держа за руку свою 
    маму. Она говорила ему о том, как важно сохранять природу и уважать окружающий мир. Вдалеке был виден силуэт 
    человека, сидящего на лавочке с книгой. Он не спешил никуда, погружённый в чтение. Вокруг царила атмосфера 
    умиротворённости и спокойствия. Солнце постепенно уходило за горизонт, окутывая парк мягким оранжевым светом. Небо 
    меняло свой цвет, переходя от светло-голубого к насыщенному розовому. Птицы готовились к ночи, прячась в ветвях 
    деревьев. Где-то рядом слышался тихий плеск воды из фонтана. Люди начинали расходиться по домам, постепенно покидая 
    парк. И вот, когда город погрузился в вечерние сумерки, наступила долгожданная тишина.
    """
    processed_text = processor.process_text(text)
    print("Результат обработки текста:")
    print(processed_text)
