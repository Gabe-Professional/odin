import json
import os
import odin.collect.munging as ocm
import odin.collect.elastic_search as ose
from tests.collect.test_elastic_search import query_path


def test_clean_data(query_path):
    creds = ose.get_creds()
    data = ose.make_api_call(creds=creds, query=query_path, index_pattern='pulse-odin*')
    df = ocm.clean_data(data)


def test_add_query_datetime(query_path):
    start_time = "2022-05-09T00:00:00.000Z"
    end_time = "2022-06-08T00:00:00.000Z"
    data = ocm.change_query_datetime(start_time=start_time, end_time=end_time, query_path=query_path)
    assert data['query']['bool']['filter'][3]['range']['system_timestamp']['gte'] == start_time
    assert data['query']['bool']['filter'][3]['range']['system_timestamp']['lte'] == end_time
