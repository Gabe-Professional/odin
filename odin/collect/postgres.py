# from odin.credentials.config import get_creds
#
#
# def create(cluster='DEV'):
import json
import logging
import os
import warnings

import pandas as pd
import psycopg2
from odin.credentials.config import BackboneProperties
logger = logging.getLogger(__name__)

# todo: replace print functions with logger...need to figure out how it works...

# todo: make this part of the class to directly apply to get_dsn

# todo: establish a simple connection, then create the helpers...


class AdminDbError(Exception):
    pass


class AdminDBWarning(UserWarning):
    pass


class Db(object):

    def __init__(self, **connection_args):
        self.logger = logging.getLogger(__name__)

        for key, value in connection_args.items():
            if value is None:
                self.logger.warning(f'POSTGRES connection argument {key} is None')
            if isinstance(value, list):
                for v in value:
                    if str(v).strip() == '':
                        self.logger.warning(f'Credentials connection argument {key} is blank'
                                            f'Check your environment variables loaded properly')
            else:
                if str(value).strip() == '':
                    self.logger.warning(f'Credentials connection argument {key} is blank. Check your'
                                        f'environment variable loaded properly')

        try:
            self._conn = psycopg2.connect(**connection_args)
        except Exception:
            msg = 'Connection to DB failed...ensure you have proper credentials and are on VPN'
            self.logger.error(msg)
            raise AdminDbError(msg)

    def __enter__(self):
        return self

    # todo: figure this out...
    def __exit__(self, t, value, traceback):
        pass

    @staticmethod
    def Create(cluster='DEV'):
        """Create a New instance of the database for a given Postgres Cluster"""
        # creds = Credentials().get_creds(cluster=cluster)
        logger.info(f'Creating database connection to Postgres {cluster}')
        bp = BackboneProperties()
        connection_info = {}
        for key in ['host', 'port', 'dbname', 'user', 'password']:
            try:
                connection_info[key] = bp[f'{cluster}_POSTGRES_{key.upper()}']
            except KeyError:
                warnings.warn(AdminDBWarning(f'Could not load {key} from Credentials. Proceeding...'))
        return Db(**connection_info)

    # todo: fix cursor spelling
    def _get_cusor(self):
        return self._conn.cursor()

    ### QUERY FUNCTIONS ###
    def get_messages_by_datetime(self, start_datetime, end_datetime, direction='in', pretty=True):
        """Helper function for getting messages from the english engagement messages table"""
        logger.info(f'Getting messages from Postgres between: {start_datetime} - {end_datetime}')
        table = "tblcApXQthi5pSGHh"
        sql = f'select "Message_ID", "Message", "DTG", "Language" from public."{table}" ' \
              f'where "Direction" in %s and "DTG" BETWEEN %s and %s'
        cursor = self._get_cusor()
        cursor.execute(sql, (tuple([direction]), tuple([start_datetime], ), tuple([end_datetime], ),))

        data = {'message_id': [],
                'message': [],
                'datetime': [],
                'language': []
                }

        for res in cursor:
            data['message_id'].append(res[0])
            data['message'].append(res[1])
            data['datetime'].append(res[2])
            data['language'].append(res[3])

        if pretty:
            data = pd.DataFrame(data)
            logger.info(f'\nPretty Data: \n {data.head(n=10)}')
        elif not pretty:
            data = data
            logger.info(f'\nNot Pretty Data: \n{data}')

        cursor.close()
        return data

    def query(self, query_statement, query_parameters):

        # todo: make a unit test for this...
        cursor = self._get_cusor()
        cursor.execute(query_statement, query_parameters)
        val = cursor.fetchall()
        cursor.close()
        return val

    def get_lastest_inbound_time_from_contact(self, contact_name, table):

        data = []
        if table is None:
            print('Please provide a table to query')

        elif table is not None:

            sql = f'select "Subject_ID", "Latest_Inbound" from public."{table}" ' \
                  f'where "Subject_ID" in %s'
            cursor = self._get_cusor()
            cursor.execute(sql, (tuple([contact_name]), ))
            data = cursor.fetchall()

            cursor.close()
        return data

