import pandas as pd
import pytest
import os
from odin.collect.elastic_search import get_query_from_path, Db, make_pretty_df, build_body_kw_query
from tests.fixture import query_path, start_time, end_time, elasticsearch_query_path, tmp_dir
import logging
import shutil
import subprocess
from datetime import timedelta
import warnings
logger = logging.getLogger(__name__)
"""
# Run test example:

pytest tests/module/file.py::test_function_name
"""


def test_progress_bar(tmp_dir):
    # todo: need to query less data
    cmd = 'odin collect '
    cmd += f'--elastic -d {tmp_dir} -sd test1 test2 -a 2023-08-11T00:00:10.000Z -b 2023-08-11T00:05:00.000Z -c PROD -kw biden nato'
    output = subprocess.check_output(cmd, shell=True)
    for o in str(output, 'UTF-8').split('\n'):
        print(o)

    string = str(output, 'UTF-8')
    assert 'Elapsed' in string
    assert os.path.exists(tmp_dir)
    shutil.rmtree(tmp_dir)


def test_get_query_from_path(elasticsearch_query_path):
    query = get_query_from_path(elasticsearch_query_path)
    assert 'query' in query.keys(), 'query not in query dict'


def test_elasticsearch_connection(elasticsearch_query_path):
    logger.info('Testing Credentials DB Connection')
    cluster = 'PROD'
    with Db.Create(cluster) as es:
        status = es.connected
    assert status, 'Elastic search is not connected'


def test_query(start_time, end_time):
    st = start_time
    et = end_time
    query = build_body_kw_query(keywords=['biden', 'nato'], start_time=st, end_time=et)

    with Db.Create('PROD') as es:
        count = es.count(query, index_pattern='pulse')
        data = es.query(query=query, index_pattern='pulse')
    assert len(data) != 0, 'QUERY did not return any data'
    assert len(data) == count, 'QUERY and COUNT did not return the same amount of data'


def test_build_body_kw_query(start_time, end_time):
    keywords = ['biden', 'nato']
    st = start_time
    et = end_time
    query = build_body_kw_query(keywords=keywords, start_time=st, end_time=et)
    assert query['query']['bool']['filter'][0]['range']['norm.timestamp']['gte'] == st
    assert query['query']['bool']['filter'][0]['range']['norm.timestamp']['lte'] == et
    kw_str = query['query']['bool']['must'][0]['query_string']['query']
    for item in keywords:
        assert item in kw_str


def test_count(start_time, end_time):
    cluster = 'PROD'
    kw = ['biden', 'nato']
    query = build_body_kw_query(keywords=kw, start_time=start_time, end_time=end_time)
    with Db.Create(cluster) as es:
        size = es.count(index_pattern='pulse', query=query)
    assert type(size) == int
