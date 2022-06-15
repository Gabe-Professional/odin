# import odin.collect.munging as ocm
import odin.utils.munging as ocm
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
    df = ocm.clean_data(data)


def test_add_query_datetime(query_path, start_time, end_time):
    start_time = start_time
    data = ocm.change_query_datetime(start_time=start_time, end_time=end_time, query_path=query_path)
    assert data['query']['bool']['filter'][3]['range']['system_timestamp']['gte'] == start_time
    assert data['query']['bool']['filter'][3]['range']['system_timestamp']['lte'] == end_time