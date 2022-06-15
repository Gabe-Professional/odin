import pytest
import os
import odin.collect.elastic_search as oce
import odin.utils.munging as ocm
from tests.fixture import query_path, start_time, end_time
"""
# Run test example:

pytest tests/module/file.py::test_function_name
"""


def test_test():
    print('test test')


def test_make_api_call(query_path, start_time, end_time):
    creds = oce.get_creds()
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
