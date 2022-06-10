import pytest
import os
import odin.collect.elastic_search as oce
import odin.collect.munging as ocm
from tests.fixture import query_path

"""
# Run test example:

pytest tests/module/file.py::test_function_name
"""
#  todo: make a file of pytest fixtures....
# start_date = "2022-05-09T00:00:00.000Z"
# end_date = "2022-06-08T00:00:00.000Z"

# @pytest.fixture
# def query_path():
#     return os.path.join(os.path.dirname(__file__), '..', 'query', 'test_rfj_alerting.json')


def test_test():
    print('test test')


def test_make_api_call(query_path):
    creds = oce.get_creds()

    start_time = "2022-05-08T00:00:00.000Z"
    end_time = "2022-05-09T00:00:00.000Z"
    # Test original file query
    data = oce.make_api_call(creds=creds, query=query_path, index_pattern='pulse-odin*')
    assert len(data) > 0
    assert {'uid', 'doc', 'system_timestamp', 'norm_attribs', 'type', 'norm', 'organization_id', 'sub_organization_id',
            'campaign_id', 'project_id', 'project_version_id', 'meta'} == set(data[0]['_source'].keys())

    # Test the query after changing the datetimes
    query = ocm.change_query_datetime(start_time=start_time, end_time=end_time, query_path=query_path)
    data = oce.make_api_call(creds=creds, query=query, index_pattern='pulse-odin*')
    assert len(data) > 0
    assert {'uid', 'doc', 'system_timestamp', 'norm_attribs', 'type', 'norm', 'organization_id', 'sub_organization_id',
            'campaign_id', 'project_id', 'project_version_id', 'meta'} == set(data[0]['_source'].keys())

    # Test that the data attributes have not changed

    # Todo: need to make the function return the gateway code, i.e 200
    # Todo: make the warnings go away...may need to use requests module.
