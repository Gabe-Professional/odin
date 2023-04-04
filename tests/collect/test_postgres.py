import odin.collect.postgres as pg
import logging
import pandas as pd
from odin.collect.postgres import Db
from tests.fixture import start_time, end_time
logger = logging.getLogger(__name__)


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



def test_get_latest_inbound_time_from_contact():
    contact_name = 'EN8211'
    table = 'tblc88A79sJPpnSyW'
    with Db.Create('DEV') as db:
        data = db.get_lastest_inbound_time_from_contact(contact_name=contact_name, table=table)

    # todo: what to assert here? data could actually be none
