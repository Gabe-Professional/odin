import logging
import warnings
import pandas as pd
import psycopg2
import functools
import time
import sys
from multiprocessing.pool import ThreadPool
from odin.credentials.config import BackboneProperties
logger = logging.getLogger(__name__)


class AdminDbError(Exception):
    pass


class AdminDBWarning(UserWarning):
    pass


def progress_bar(func):
    def time_it(i):
        time.sleep(1)
        length = 60
        i += 1
        bar = length
        if i == length + 1:
            i = 1
        # sys.stdout.write('\r{}'.format('.' * i))
        sys.stdout.write('\r{} Elapsed time: {}'.format('█' * i + '-' * (length - i), i))

        sys.stdout.flush()
        return i

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print("Running process: {}".format(func.__name__))
        proc_start = time.time()
        pool = ThreadPool(processes=1)
        t1 = pool.apply_async(func, args, kwargs)  # tuple of args for foo
        i = 0
        while not t1.ready():
            i = time_it(i)
        v = t1.get()
        sys.stdout.write('\n')
        proc_stop = time.time()
        logger.debug("Process {} took {} seconds to run.".format(func.__name__, proc_stop - proc_start))
        pool.close()
        return v

    return wrapper


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
    def get_column_names(self, table_name: str):
        tables = ['adjectives', 'annotations', 'attachment_release_requests', 'attachments', 'audit', 'codenames'
                  'contact_core_annotations', 'contacts', 'dropdown_options', 'locked_rows', 'messages']
        if table_name not in tables:
            raise ValueError(f'Please input a valid table name from: {", ".join(tables)}')
        else:
            cursor = self._get_cursor()
            sql = f"select column_name from information_schema.columns where table_name = '{table_name}';"
            cursor.execute(sql)

            column_names = [result[0] for result in cursor.fetchall()]
            cursor.close()

        return column_names



    @progress_bar
    def query(self, query_statement, query_parameters):

        # todo: make a unit test for this...
        cursor = self._get_cursor()
        cursor.execute(query_statement, (tuple(query_parameters),))
        val = cursor.fetchall()
        cursor.close()
        return val

    @progress_bar
    def get_random_messages_in(self, fields=None, size=100):
        # todo: maybe can expand this function to other tables as well...
        default_fields = ['message_id', 'timestamp', 'contact_id', 'message', 'direction', 'machine_translation']
        table = 'messages'
        if fields is None:
            fields = default_fields
        elif not isinstance(fields, list):
            raise ValueError('Argument fields must be a list')
        field_str = ', '.join(fields)
        direction = 'in'
        sql = f'select setseed(1); ' \
              f'select {field_str} from public.{table} ' \
              f'where direction in %s ' \
              f'order by random() limit %s;'

        cursor = self._get_cursor()
        cursor.execute(sql, (tuple([direction]), tuple([size])))

        df = pd.DataFrame(data=cursor.fetchall(), columns=fields)
        return df

    @progress_bar
    def get_messages_by_datetime(self, start_datetime, end_datetime, direction='in', fields=None, pretty=True):
        """Helper function for getting messages from the english engagement messages table"""
        logger.info(f'Getting messages from Postgres between: {start_datetime} - {end_datetime}')
        table = "messages"
        default_fields = ['message_id', 'timestamp', 'contact_id', 'message', 'direction', 'machine_translation']
        if fields is None:
            fields = default_fields
        elif not isinstance(fields, list):
            raise ValueError('Argument fields must be a list')
        field_str = ', '.join(fields)
        sql = f'select {field_str} ' \
              f'from public."{table}" ' \
              f'where "direction" in %s and "timestamp" BETWEEN %s and %s'
        cursor = self._get_cursor()
        cursor.execute(sql, (tuple([direction]), tuple([start_datetime], ), tuple([end_datetime], ),))
        # todo: add field inputs from user, if none provide default list
        data = cursor.fetchall()
        if pretty:
            data = pd.DataFrame(data=data, columns=fields)
            logger.info(f'\nPretty Data: \n {data.head(n=10)}')
        elif not pretty:
            data = data
            logger.info(f'\nNot Pretty Data: \n {data}')

        cursor.close()
        return data

    @progress_bar
    def get_messages_from_contact_id(self, *contact_id, pretty=True, direction=None):
        table = "messages"
        fields = ["message_id", "contact_id", "message", "machine_translation", "timestamp", "direction"]

        if direction is None:
            sql = f'select {",".join(fields)} from public.{table} where contact_id in %s'
            cursor = self._get_cursor()
            cursor.execute(sql, (tuple(contact_id),))
        else:
            sql = f'select {",".join(fields)} from public.{table} where contact_id in %s and direction=%s'
            cursor = self._get_cursor()
            cursor.execute(sql, (tuple(contact_id), tuple([direction])), )

        data = cursor.fetchall()
        if pretty:
            data = pd.DataFrame(data=data, columns=fields)
        cursor.close()
        return data

    @progress_bar
    def get_contacts_by_datetime(self, start_datetime, end_datetime, pretty=True):
        table = "contacts"
        fields = ["contact_id", "contact_urn", "created_datetime"]
        sql = f'select {",".join(fields)} from public."{table}" ' \
              f'where "created_datetime" BETWEEN %s and %s'
        cursor = self._get_cursor()
        cursor.execute(sql, (tuple([start_datetime], ), tuple([end_datetime], ),))
        data = cursor.fetchall()

        if pretty:
            data = pd.DataFrame(data=data, columns=fields)

        return data

    def get_contact_rating(self, *contact_id):

        table = 'annotations'
        value = ['A', 'B', 'C', 'D', 'E', 'F', 'G']
        sql = f'select contact_id, annotation_name, annotation_value from public.{table} ' \
              f'where annotation_value in %s AND contact_id in %s'
        cursor = self._get_cursor()
        cursor.execute(sql, (tuple(value, ), tuple(contact_id, ),))
        data = cursor.fetchall()
        data = {str(t[0]): str(t[2]) for t in data}

        cursor.close()
        return data
