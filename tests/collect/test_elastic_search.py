import pytest
import os
import odin.collect.elastic_search as oce

from odin.collect import elastic_search



"""
# Run test example:

pytest tests/module/file.py::test_function_name
"""

@pytest.fixture
def query():
    return os.path.join(os.path.dirname(__file__), '..', 'query', 'test_rfj_alerting.json')

def test_test():
    print('test test')

def test_make_api_call(query):
    creds = oce.get_creds()
    data = oce.make_api_call(creds=creds, query_file_path=query, index_pattern='pulse-odin*')

    # Test that the data attributes have not changed
    assert {'uid', 'doc', 'system_timestamp', 'norm_attribs', 'type', 'norm', 'organization_id', 'sub_organization_id',
            'campaign_id', 'project_id', 'project_version_id', 'meta'} == set(data[0]['_source'].keys())
    # Todo: need to make the function return the gateway code, i.e 200
    # Todo: make the warnings go away...may need to use requests module.
