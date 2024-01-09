# import odin.collect.munging as oum
import pandas as pd

import odin.utils.munging as oum
import odin.collect.elastic_search as ose
from tests.conftest import query_path, start_time, end_time, name_labels, names_data_csv


strg = "[0.015952223911881447, 0.029908902943134308, -0.062116459012031555, -0.06531211733818054, " \
       "0.040432073175907135, -0.01862291246652603, -0.03856552764773369, 0.010605946183204651, " \
       "0.034261252731084824, 0.0022553682792931795, -0.011359820142388344, -0.006993964780122042, " \
       "-0.05275590717792511, -0.021328287199139595]"


# def test_text_tokenize():
#     # todo: this test may be failing in docker because the function uses a stopword dictionary
#     #  that does not exist in the docker container
#     string = 'This is a picture of a CAT!!! But not really :)...And I would like a picture of a dog'
#     lem = oum.text_tokenize(string, add_stopwords=['like', 'would'])
#     assert type(lem) == str
#     assert string != lem


def test_document():
    string = 'This is a PICTURE of a CAT!!! But not really :)...And I would like a picture of a dog'
    cls = oum.label_document(label_text='picture', doc_text=string)


def test_label_text_from_dict(name_labels, names_data_csv):
    test_df = pd.read_csv(names_data_csv)
    test_labels_df = pd.read_csv(name_labels)
    labels_dict = {}
    for idx in range(len(test_labels_df)):
        key, label = test_labels_df.iloc[idx, :]['name'], test_labels_df.iloc[idx, :]['label']
        labels_dict[key] = label

    for idx in range(len(test_df)):
        test_document_text = test_df.loc[idx, 'body']
        subject = oum.label_text_from_dict(document_text=test_document_text, label_dict=labels_dict)
        assert len(subject) != 0

    dct = oum.REWARD_OFFER_NAMES_DICT


def test_parse_vector_string(names_data_csv):
    string = "['strength', 'war', 'state', 'speed', 'effort', 'follow', 'give', 'inform', 'report', 'get', " \
             "'follow', 'effort', 'strength', 'war', 'state', 'give', 'meet', 'inform', 'report', 'thing', " \
             "'true', 'correct', 'certain', 'act', 'strength', 'war', 'state', 'speed', 'last', 'effort']"
    # todo: generalize this test and function better.
    df = pd.read_csv(names_data_csv)
    vl = oum.parse_vector_string(df.loc[0, 'labse_encoding'], value_type='float')

    assert isinstance(vl, list)
    assert isinstance(vl[0], float)
    vl = oum.parse_vector_string(string, value_type='str')
    assert isinstance(vl, list)
    assert isinstance(vl[0], str)


def test_preprocess_text():
    text = 'This is a message that contains some stop words and custom WORDS to Remove from TEXT messages the text ' \
           'should be in a list format when do so it can be processed by LDA helpers. This text processor should also ' \
           'remove a set of custom stopwords provided. It should remove the words Video, Photo, and Custom. This ' \
           'should also lemmatize words. For example words should map to word and cats should map to cat. Jogging ' \
           'should also map or maps to jog. The custom stem list should map syrian to syria...well see...'
    custom_words = ['video', 'photo', 'custom']
    lems_stems = ['cats', 'words', 'jogging']
    custom_stem = {'syrian': 'syria'}
    domain_words = ['syria']
    # Test the stemming feature
    new_text = oum.preprocess_text(text, custom_stem=custom_stem, domain_words=domain_words, custom_stopwords=custom_words, token=('stem',))
    list_text = text.split(' ')
    # Assert removal of stopwords
    assert len(new_text) < len(list_text)

    # Assert removal of custom stopwords
    for word in custom_words:
        assert word not in new_text
    for stem, root in zip(custom_stem.keys(), custom_stem.values()):
        assert stem not in new_text
        assert root in new_text

    # Assert that stemming occurred.
    for word in lems_stems:
        assert word not in new_text


def test_get_domain_words(domain_kw_fp):
    kwds = oum.get_domain_words(domain_kw_fp)
    assert isinstance(kwds, list)


def test_make_topic_str():
    lda_list = [(0, '0.005*"aword1" + 0.005*"word2" + 0.005*"bword3" + 0.004*"word4" + 0.004*"cword5" + 0.004*"word6"'),
                (1, '0.005*"word1" + 0.005*"word2" + 0.005*"word3" + 0.004*"word4" + 0.004*"word5" + 0.004*"word6"'),
                (2, '0.005*"word1" + 0.005*"word2" + 0.005*"word3" + 0.004*"word4" + 0.004*"word5" + 0.004*"word6"')]

    lda_str = oum.make_topic_str(lda_topics=lda_list)

    assert 'topic' in lda_str.lower()
    assert 'word' in lda_str.lower()
