# import odin.collect.munging as oum
import pandas as pd

import odin.utils.munging as oum
import odin.collect.elastic_search as ose
from tests.fixture import query_path, start_time, end_time, name_labels, names_data_csv


strg = "[0.015952223911881447, 0.029908902943134308, -0.062116459012031555, -0.06531211733818054, " \
       "0.040432073175907135, -0.01862291246652603, -0.03856552764773369, 0.010605946183204651, " \
       "0.034261252731084824, 0.0022553682792931795, -0.011359820142388344, -0.006993964780122042, " \
       "-0.05275590717792511, -0.021328287199139595]"


# todo: update clean data function test...import the saved data, not query new data.
def test_clean_data(query_path):
    creds = ose.get_creds()
    data = ose.make_api_call(creds=creds, query=query_path, index_pattern='pulse-odin*')
    df1 = oum.clean_data(data, drop_duplicate_uids=False)
    l1 = len(df1)
    df2 = oum.clean_data(data, drop_duplicate_uids=True)
    l2 = len(df2)
    assert l1 > l2


def test_add_query_datetime(query_path, start_time, end_time):
    start_time = start_time
    data = oum.change_query_datetime(start_time=start_time, end_time=end_time, query_path=query_path)
    assert data['query']['bool']['filter'][3]['range']['system_timestamp']['gte'] == start_time
    assert data['query']['bool']['filter'][3]['range']['system_timestamp']['lte'] == end_time


def test_text_tokenize():
    # todo: make a better test for this...check removal...
    string = 'This is a picture of a CAT!!! But not really :)...And I would like a picture of a dog'
    lem = oum.text_tokenize(string, add_stopwords=['like', 'would'])
    assert type(lem) == str
    assert string != lem


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
    # for s in subject:
    #     assert s in dct
    # assert len(subject) > 0
    # assert type(subject) == list

    # test_document_text = "#REVOLUTIONARY STRUGGLE is one of the organization names, but it is not SAUDI HIZBALLAH'..." \
    #                      "this function should label the name as a label"
    # orgs = oum.label_text_from_dict(document_text=test_document_text, label_dict=oum.ORGANIZATION_NAMES_DICT)
    # dct = oum.ORGANIZATION_NAMES_DICT
    # for o in orgs:
    #     assert o in dct
    # assert len(orgs) > 0
    # assert type(orgs) == list


