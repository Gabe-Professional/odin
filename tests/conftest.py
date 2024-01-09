import pytest
import os
import logging
from datetime import datetime

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
    return os.path.join(os.path.dirname(__file__), 'data',
                        'test_names_2022-05-31 21:03:45+00:00_2022-05-31 22:56:20+00:00.csv')


@pytest.fixture
def ga_data_fp():
    return os.path.join(os.path.dirname(__file__), 'data', 'download_activity.csv')


@pytest.fixture
def contact_id_ist():
    return ['35', '443']

@pytest.fixture
def domain_kw_fp():
    return os.path.join(os.path.dirname(__file__), 'data', 'domain_kw.txt')


@pytest.fixture
def pg_log_fp():
    return os.path.join(os.path.dirname(__file__), 'collect', 'pg_tests.log')


def pytest_configure(config):
    config.addinivalue_line("markers", "custom_logging: Tests using custom logging")

@pytest.fixture(scope='session', autouse=True)
def setup_logging(request):
    if request.config.getoption("-m") and "custom_logging" not in request.config.getoption("-m"):
        return  # Skip logging setup if the marker is not present

    log_file = 'test_results.log'

    # Create a formatter with the desired format
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    # Create a file handler and set the formatter
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)

    # Get the root logger and add the file handler
    root_logger = logging.getLogger()
    root_logger.addHandler(file_handler)

    # Log start time
    start_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    logging.info(f'Tests started at: {start_time}')

    def teardown():
        # Log end time and duration
        end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        logging.info(f'Tests ended at: {end_time}')

        # Calculate and log the duration
        duration = (datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S') - datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')).total_seconds()
        logging.info(f'Duration: {duration} seconds')

    request.addfinalizer(teardown)