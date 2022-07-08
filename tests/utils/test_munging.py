# import odin.collect.munging as oum
import odin.utils.munging as oum
import odin.collect.elastic_search as ose
from tests.fixture import query_path, start_time, end_time


strg = "[0.015952223911881447, 0.029908902943134308, -0.062116459012031555, -0.06531211733818054, " \
       "0.040432073175907135, -0.01862291246652603, -0.03856552764773369, 0.010605946183204651, " \
       "0.034261252731084824, 0.0022553682792931795, -0.011359820142388344, -0.006993964780122042, " \
       "-0.05275590717792511, -0.021328287199139595]"


# def test_lst_string_to_flt():
#     lst = str_to_lst_flt(strg)
#     assert type(lst[0]) == float


def test_clean_data(query_path):
    creds = ose.get_creds()
    data = ose.make_api_call(creds=creds, query=query_path, index_pattern='pulse-odin*')
    df = oum.clean_data(data)


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


def test_get_reward_offer_subject_from_text():
    test_document_text = "#HAFIZ SAEED' is one of the reward offer subjects..." \
                         "this function should label the name as a label"
    subject = oum.label_text_from_dict(document_text=test_document_text)
    dct = oum.REWARD_OFFER_NAMES_DICT
    for s in subject:
        assert s in dct
    assert len(subject) > 0
    assert type(subject) == list

    test_document_text = "#REVOLUTIONARY STRUGGLE is one of the organization names, but it is not SAUDI HIZBALLAH'..." \
                         "this function should label the name as a label"
    orgs = oum.label_text_from_dict(document_text=test_document_text, label_dict=oum.ORGANIZATION_NAMES_DICT)
    dct = oum.ORGANIZATION_NAMES_DICT
    for o in orgs:
        assert o in dct
    assert len(orgs) > 0
    assert type(orgs) == list


