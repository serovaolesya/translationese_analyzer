from nltk.tokenize import word_tokenize

from tools.core.text_preparation import TextPreProcessor


def get_word_tokens(text):
    # Подготавливаем текст к токенизации
    preprocess = TextPreProcessor()
    preprocessed_text = preprocess.process_text(text)

    print('\n! Токенизаторы NLTK:')

    standard_tokenizer = word_tokenize(preprocessed_text)
    for t in standard_tokenizer:
        print(t)
    print('\nСтандартный токенизатор слов (воспринимает слова, пишущиеся через дефис, как одно слово):')

    print(standard_tokenizer)
    print(len(standard_tokenizer))
    return

    # print('\nТокенизатор слов и пунктуации (а этот делит и такие слова на отдельные части):')
    # wp_tokenizer = WordPunctTokenizer()
    # tokens = wp_tokenizer.tokenize(input_text)
    #
    # print('\nТокенизатор WordPunctTokenizer:')
    # print(tokens)
    # print(len(tokens))

    # print('\nТокенизатор по регулярным выражениям:')
    # tokenizer = RegexpTokenizer(r'\w+|$[0-9.]+|\S+')
    # print(tokenizer.tokenize('Don't hesitate 77 to ask questions'))

    # Создаем экземпляр токенизатора NIST
    # nist_tokenizer = NISTTokenizer()
    #
    # nist_tokens = nist_tokenizer.tokenize(input_text)
    # print('\nТокенизатор NIST Tokens для BLEU (прилепляет ковычки к словам):')
    # print(nist_tokens)
    # print(len(nist_tokens))

    # print('\n! Токенизаторы spaCy:\n')
    #
    # nlp_model = spacy.load('ru_core_news_lg')
    #
    # text_doc = nlp_model(preprocessed_text)
    #
    # # Создание списка токенов для всего текста
    # spacy_tokens = [token.text for token in text_doc]
    #
    # print(spacy_tokens)
    # print(len(spacy_tokens))

# print('\n! Токенизатор И. Козиева:\n')
#
# koziev_tokenizer = rutokenizer.Tokenizer()
# koziev_tokenizer.load()
# koziev_tokens = koziev_tokenizer.tokenize(input_text)
#
# print(koziev_tokens)
# print(len(koziev_tokens))


if __name__ == "__main__":
    # Проверяем!
    get_word_tokens(input('Введите текст для анализа:\n'))

