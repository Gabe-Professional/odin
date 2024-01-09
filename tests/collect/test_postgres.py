from datetime import datetime
import logging
import time

import pandas as pd
import pytest

from odin.collect.postgres import Db
import subprocess
import shutil
import os
logger = logging.getLogger(__name__)

# logging.basicConfig(filename='test_pg.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# todo: future addition to pg testing. Logging runs.
# @pytest.mark.custom_logging
# def test_log_file():
#     start = datetime.now()
#     try:
#         logging.error(f'Start: {start}')
#         time.sleep(3)
#         end = datetime.now()
#         logging.error(f'End: {end}')
#
#         assert 1 == 2, 'Test failed...'
#
#         # logging.info(f'{timestamp} Example passed')
#     except AssertionError as e:
#         logging.error(f'Test Example: Failed - {e}')


# def test_log_file(pg_log_fp):
#     with open(pg_log_fp, 'a') as f:
#         f.write(f'TEST NAME: PG TEST NAME\n')
#         f.write(f'START TIME: {datetime.now()}\n')
#         time.sleep(5)
#         f.write(f'END TIME: {datetime.now()}\n')
#
#     assert os.path.exists(pg_log_fp)


def test_progress_bar(tmpdir, start_time, end_time):

    subdirs = ['test_1', 'test_2']
    cmd = 'odin collect '
    cmd += f'--postgres -d {tmpdir} -sd {subdirs[0]} {subdirs[1]} ' \
           f'-a {start_time} -b {end_time} -i'

    output = subprocess.check_output(cmd, shell=True)
    for o in str(output, 'UTF-8').split('\n'):
        print(o)

    string = str(output, 'UTF-8')
    assert 'Elapsed' in string
    assert os.path.exists(tmpdir)
    shutil.rmtree(tmpdir)


def test_db_connection(start_time, end_time):
    logger.info('Testing Credentials DB Connection')

    st = start_time
    et = end_time
    # todo: could use the db as a pytest fixture
    with Db.Create('DEV') as db:
        data = db.get_messages_by_datetime(start_datetime=st, end_datetime=et, direction='in')

    df = data
    assert len(df) > 0


def test_get_random_messages_in(pg_log_fp):
    test_start = datetime.now()

    # todo: Test bad fields type
    size = 150
    fields = ['message_id', 'timestamp', 'direction']
    with Db.Create('DEV') as pg:
        df = pg.get_random_messages_in(fields=fields, size=size)

    assert set(fields) == set(df.columns)
    assert len(df) == size
    assert df['direction'].unique() == 'in'


def test_get_messages_by_datetime(start_time, end_time):
    st = start_time
    et = end_time
    with Db.Create('DEV') as db:
        df = db.get_messages_by_datetime(start_datetime=st, end_datetime=et, direction='in', pretty=True)
        data = db.get_messages_by_datetime(start_datetime=st, end_datetime=et, direction='in', pretty=False)

    assert len(df) > 0
    assert len(data) > 0
    assert isinstance(df, pd.DataFrame)
    assert isinstance(data, list)


def test_get_messages_from_contact_id():
    contact_id = ['35', '443']

    pretty = True
    if pretty:
        with Db.Create('DEV') as db:
            df = db.get_messages_from_contact_id(*contact_id, pretty=pretty)
            dir_df = db.get_messages_from_contact_id(*contact_id, pretty=pretty, direction='in')
        assert type(df) == pd.DataFrame
        assert len(df) != 0
        assert len(df) > len(dir_df)
        assert dir_df['direction'].unique() == ['in']

    pretty = False
    if not pretty:
        with Db.Create('DEV') as db:
            data = db.get_messages_from_contact_id(*contact_id, pretty=pretty)
            dir_df = db.get_messages_from_contact_id(*contact_id, pretty=pretty, direction='in')

        assert type(data) == list
        assert len(data) != 0
        assert len(df) > len(dir_df)


def test_get_contacts_by_datetime(start_time, end_time):
    st = start_time
    et = end_time

    pretty = True
    if pretty:
        with Db.Create('DEV') as db:
            df = db.get_contacts_by_datetime(start_datetime=st, end_datetime=et, pretty=pretty)
        assert len(df) != 0
        assert len(df.columns) == 3
        assert type(df) == pd.DataFrame

    pretty = False
    if not pretty:
        with Db.Create('DEV') as db:
            data = db.get_contacts_by_datetime(start_datetime=st, end_datetime=et, pretty=pretty)
        assert len(data) != 0
        assert len(data[0]) == 3
        assert type(data) == list


def test_get_column_names():

    valid_table_name = 'messages'
    invalid_table_name = 'stuff'
    with Db.Create('DEV') as pg:
        with pytest.raises(ValueError, match='Please input a valid table name'):
            pg.get_column_names(table_name=invalid_table_name)
        columns = pg.get_column_names(table_name=valid_table_name)
        assert isinstance(columns, list)
        assert len(columns) > 0


def test_query():
    # query_statement = f'select contact_id, annotation_name, annotation_value from public.annotations ' \
    #                   f'where annotation_value in %s'
    # ratings = ['A', 'B', 'C', 'D', 'E', 'F', 'G']
    # with Db.Create('DEV') as pg:
    #     contacts = pg.query(query_statement=query_statement, query_parameters=ratings)
    #     print(contacts)
    pass


def test_get_contact_rating():
    contacts = ['13429', '16538']
    with Db.Create('DEV') as pg:
        data = pg.get_contact_rating(*contacts)
        print(data)

    assert set(data.keys()) == set(contacts)