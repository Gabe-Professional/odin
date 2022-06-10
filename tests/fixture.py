import pytest
import os

@pytest.fixture
def query_path():
    return os.path.join(os.path.dirname(__file__), 'query', 'test_rfj_alerting.json')
