import logging
import pandas as pd
from odin.collect.postgres import Db
import subprocess
import shutil
import os
logger = logging.getLogger(__name__)


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


def test_get_messages_by_datetime(start_time, end_time):
    st = start_time
    et = end_time
    with Db.Create('DEV') as db:
        df = db.get_messages_by_datetime(start_datetime=st, end_datetime=et, direction='in', pretty=True)
        data = db.get_messages_by_datetime(start_datetime=st, end_datetime=et, direction='in', pretty=False)

    assert len(df) > 0
    assert len(data.values()) > 0


def test_get_messages_from_contact_id():
    contact_id = ['35', '443']

    pretty = True
    if pretty:
        with Db.Create('DEV') as db:
            df = db.get_messages_from_contact_id(*contact_id, pretty=pretty)
        assert type(df) == pd.DataFrame
        assert len(df) != 0

    pretty = False
    if not pretty:
        with Db.Create('DEV') as db:
            data = db.get_messages_from_contact_id(*contact_id, pretty=pretty)
        assert type(data) == list
        assert len(data) != 0


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

