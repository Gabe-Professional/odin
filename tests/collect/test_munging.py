import odin.collect.munging as ocm
import odin.collect.elastic_search as ose
from tests.fixture import query_path, start_time, end_time


def test_clean_data(query_path):
    creds = ose.get_creds()
    data = ose.make_api_call(creds=creds, query=query_path, index_pattern='pulse-odin*')
    df = ocm.clean_data(data)


def test_add_query_datetime(query_path, start_time, end_time):
    start_time = start_time
    data = ocm.change_query_datetime(start_time=start_time, end_time=end_time, query_path=query_path)
    assert data['query']['bool']['filter'][3]['range']['system_timestamp']['gte'] == start_time
    assert data['query']['bool']['filter'][3]['range']['system_timestamp']['lte'] == end_time
