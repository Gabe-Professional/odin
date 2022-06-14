import pytest
import os

@pytest.fixture
def query_path():
    return os.path.join(os.path.dirname(__file__), 'query', 'test_rfj_alerting.json')

@pytest.fixture
def start_time():
    return "2022-05-09T00:00:00.000Z"

@pytest.fixture
def end_time():
    return "2022-06-08T00:00:00.000Z"
