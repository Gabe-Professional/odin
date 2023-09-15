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

    # todo: generalize this test and function better.
    df = pd.read_csv(names_data_csv)
    vl = oum.parse_vector_string(df.loc[0, 'labse_encoding'])

    assert type(vl) == list
    assert type(vl[0]) == float

