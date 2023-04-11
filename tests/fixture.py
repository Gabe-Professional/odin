import pytest
import os


@pytest.fixture
def query_path():
    return os.path.join(os.path.dirname(__file__), 'query', 'test_rfj_alerting.json')


@pytest.fixture
def elasticsearch_query_path():
    return os.path.join(os.path.dirname(__file__), 'query', 'test_elasticsearch_query.json')

@pytest.fixture
def start_time():
    return "2022-12-09T00:00:00.000Z"


@pytest.fixture
def end_time():
    return "2022-12-11T00:00:00.000Z"


@pytest.fixture
def name_labels():
    return os.path.join(os.path.dirname(__file__), 'data', 'test_name_labels.csv')


@pytest.fixture
def names_data_csv():
    return os.path.join(os.path.dirname(__file__), 'data', 'test_names_2022-05-31 21:03:45+00:00_2022-05-31 22:56:20+00:00.csv')


@pytest.fixture
def tmp_dir():
    return '/tmp/test_setup'
