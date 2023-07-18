import pandas as pd
import pytest
import os
from odin.collect.elastic_search import get_query_from_path, Db, make_pretty_df, build_body_kw_query
from tests.fixture import query_path, start_time, end_time, elasticsearch_query_path
import logging
from datetime import timedelta
import warnings
logger = logging.getLogger(__name__)
"""
# Run test example:

pytest tests/module/file.py::test_function_name
"""


def test_get_query_from_path(elasticsearch_query_path):
    query = get_query_from_path(elasticsearch_query_path)


def test_elasticsearch_connection(elasticsearch_query_path):

    query = get_query_from_path(elasticsearch_query_path)
    logger.info('Testing Credentials DB Connection')
    cluster = 'PROD'

    fields = ['uid', 'timestamp', 'author', 'body', 'domain', 'encoding', 'url']
    custom_fields = ['uid', 'url', 'author_id']

    size = 10
    with Db.Create(cluster) as es:
        data = es.query(query=query, index_pattern='pulse', search_after=False, batch_size=size)
        pd.set_option('display.max_columns', None)

        df = make_pretty_df(data)
        df1 = make_pretty_df(data, fields=custom_fields)

    # TEST DEFAULT FIELDS
    assert len(df) == size
    assert set(df.columns) == set(fields)

    # TEST CUSTOM FIELDS
    assert len(df1) == size
    assert set(df1.columns) == set(custom_fields)


def test_query(start_time, end_time):
    st = start_time
    et = end_time
    query = build_body_kw_query(keywords=['biden', 'nato'], start_time=st, end_time=et)

    with Db.Create('PROD') as es:
        count = es.count(query, index_pattern='pulse')
        data = es.query(query=query, index_pattern='pulse', search_after=True, batch_size=100)
        df = make_pretty_df(data)
    assert count == len(df) == len(data)


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
