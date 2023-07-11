import logging
import warnings
import pandas as pd
import psycopg2
from odin.credentials.config import BackboneProperties
logger = logging.getLogger(__name__)


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

    def _get_cursor(self):
        return self._conn.cursor()

    ### QUERY FUNCTIONS ###
    def get_messages_by_datetime(self, start_datetime, end_datetime, direction='in', pretty=True):
        """Helper function for getting messages from the english engagement messages table"""
        logger.info(f'Getting messages from Postgres between: {start_datetime} - {end_datetime}')
        table = "messages"
        sql = f'select "message_id", "message", "timestamp", "engage_org" from public."{table}" ' \
              f'where "direction" in %s and "timestamp" BETWEEN %s and %s'
        cursor = self._get_cursor()
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
        cursor = self._get_cursor()
        cursor.execute(query_statement, query_parameters)
        val = cursor.fetchall()
        cursor.close()
        return val

    def get_messages_from_contact_id(self, contact_id, pretty=True):
        table = "messages"
        # data = []
        fields = ["contact_id", "message", "timestamp"]
        sql = f'select {",".join(fields)} from public.{table} where "contact_id" in %s'
        cursor = self._get_cursor()
        cursor.execute(sql, (tuple([contact_id]),))
        data = cursor.fetchall()
        if pretty:
            data = pd.DataFrame(data=data, columns=fields)

        cursor.close()
        return data

    def get_contacts_by_datetime(self, start_datetime, end_datetime, pretty=True):
        table = "contacts"
        fields = ["contact_id", "contact_urn", "created_time"]
        sql = f'select {",".join(fields)} from public."{table}" ' \
              f'where "created_time" BETWEEN %s and %s'
        cursor = self._get_cursor()
        cursor.execute(sql, (tuple([start_datetime], ), tuple([end_datetime], ),))
        data = cursor.fetchall()

        if pretty:
            data = pd.DataFrame(data=data, columns=fields)

        return data
