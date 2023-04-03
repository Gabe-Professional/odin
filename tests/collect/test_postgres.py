import odin.collect.postgres as pg
import logging
import pandas as pd
from odin.collect.postgres import Db
logger = logging.getLogger(__name__)


def test_db_connection():
    logger.info('Testing Credentials DB Connection')

    start_datetime = '2023-02-26T00:00:00'
    end_datetime = '2023-02-27T00:00:00'
    # todo: could use the db as a pytest fixture
    with Db.Create('DEV') as db:
        data = db.get_messages_by_datetime(start_datetime=start_datetime, end_datetime=end_datetime, direction='in')

    df = pd.DataFrame(data)
    assert len(df) > 0


def test_get_latest_inbound_time_from_contact():
    contact_name = 'EN8211'
    table = 'tblc88A79sJPpnSyW'
    with Db.Create('DEV') as db:
        data = db.get_lastest_inbound_time_from_contact(contact_name=contact_name, table=table)

    # todo: what to assert here? data could actually be none
