import logging
import functools
import sys
import time
import os
import json
import pandas as pd
from odin.credentials.config import BackboneProperties
from elasticsearch import Elasticsearch
import warnings
from elasticsearch.exceptions import ElasticsearchWarning
from multiprocessing.pool import ThreadPool
logger = logging.getLogger(__name__)
cwd = os.getcwd()


def get_query_from_path(filepath):
    with open(filepath, 'r') as fp:
        query = json.load(fp)
    return query


class AdminDbError(Exception):
    pass


class AdminDBWarning(UserWarning):
    pass


def parse_url(username, password, endpoint):
    url = ['https://{}:{}@{}'.format(username, password, endpoint[8:])]
    return url


def make_pretty_df(data, fields=[]):

    # todo: need to account for times when no data returned...
    # todo: need to add meta fields when necessary...
    norm_fields = ['author', 'domain', 'id', 'body', 'author_id', 'url', 'timestamp']
    meta_fields = []
    labse_fields = ['clean_text_length', 'encoding']

    if len(fields) == 0:
        fields = ['uid', 'timestamp', 'author', 'body', 'domain', 'encoding', 'url']
        tmp = {f: [] for f in fields}
        logger.info(f'No fields provided, setting to default: {fields}')

    else:
        tmp = {f: [] for f in fields}

    for res in data:
        for f in fields:
            if f in norm_fields:
                try:
                    tmp[f].append(res['_source']['norm'][f])
                except:
                    tmp[f].append(None)

            elif f in labse_fields:
                try:
                    tmp[f].append(res['_source']['meta']['ml_labse'][0]['results'][0][f])

                except:
                    tmp[f].append(None)
            else:
                try:
                    tmp[f].append(res['_source'][f])
                except:
                    tmp[f].append(None)
    df = pd.DataFrame(tmp)
    return df


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
        self.connected = False
        for key, value in connection_args.items():
            if value is None:
                self.logger.warning(f'ELASTIC connection argument {key} is None')
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
            url = parse_url(username=connection_args['username'],
                            password=connection_args['password'],
                            endpoint=connection_args['endpoint'])
            self._conn = Elasticsearch(url)

            ## IGNORE THE ELASTICSEARCH SERVER WARNING ##
            warnings.simplefilter('ignore', ElasticsearchWarning)

        except Exception:
            msg = 'Connection to DB failed...ensure you have proper credentials'
            self.logger.error(msg)
            raise AdminDbError(msg)

        self.connected = True

    def __enter__(self):
        return self

    def __exit__(self, t, value, traceback):
        pass

    @staticmethod
    def Create(cluster='DEV'):
        """Create a New instance of the database for a given Postgres Cluster"""

        logger.info(f'Creating database connection to Elastic {cluster}')
        bp = BackboneProperties()
        connection_info = {}
        for key in ['username', 'password', 'endpoint']:
            try:
                connection_info[key] = bp[f'{cluster}_ELASTIC_{key.upper()}']
            except KeyError:
                warnings.warn(AdminDBWarning(f'Could not load {key} from Credentials. Proceeding...'))

        return Db(**connection_info)

    @progress_bar
    def query(self, query, index_pattern):
        """Helper function to query Elasticsearch easily...
        """
        search_after = True
        batch_size = None
        warnings.simplefilter(action='ignore')
        if type(query) == str:
            with open(query) as f:
                query = json.load(f)
        elif type(query) == dict:
            query = query
        count = self.count(query=query, index_pattern=index_pattern)
        data = []
        logger.info(f'Your query has {count} results')
        if count < 10000:
            logger.info('Setting batch size to max records...10,000')
            results = self._conn.search(index=index_pattern, query=query['query'], size=10000)
            data = results['hits']['hits'][:]
        else:
            logger.info(f'Results count is greater than 10k. Batching your query, please wait...')
            if search_after:
                if not batch_size:
                    batch_size = 1000
                    logger.info(f'Setting default batch size to {batch_size}...')

                results = self._conn.search(index=index_pattern, query=query['query'], size=batch_size, sort='system_timestamp')
                tmp = results['hits']['hits'][0]

                data = results['hits']['hits'][:]
                _sys_time = results['hits']['hits'][batch_size - 1]['_source']['system_timestamp']

                logging.info('Batching data from Elasticsearch...')
                # todo: something is still kind of weird here...does not get the last batch sometimes...
                #  just adding the first value again to get around...not a huge deal for now.
                while count > len(data):
                    results = self._conn.search(index=index_pattern, query=query['query'],
                                                size=batch_size, sort='system_timestamp', search_after=[_sys_time])
                    current_batch = len(results['hits']['hits'][:])
                    try:
                        _sys_time = results['hits']['hits'][current_batch - 1]['_source']['system_timestamp']
                        data += results['hits']['hits'][:]
                    except:
                        # _sys_time = results['hits']['hits'][0]['_source']['system_timestamp']
                        data += tmp

        logger.info(f'Elasticsearch returned {len(data)} results')
        return data

    def count(self, query, index_pattern):
        if type(query) == str:
            with open(query) as f:
                query = json.load(f)
        elif type(query) == dict:
            query = query

        size = self._conn.count(index=index_pattern, query=query['query'])['count']
        return size


# SOME HELPERS TO BUILD DSL QUERIES
def build_body_kw_query(keywords: list, start_time, end_time):
    # todo: add checking for datetime format...
    dsl_fp = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'query', 'keyword_query_template.json')
    query = get_query_from_path(dsl_fp)
    kw_string = 'norm.body: (\"' + '\" OR \"'.join(keywords) + '\")'
    # todo: add user timezone
    tz = "Europe/London"
    query['query']['bool']['must'][0]['query_string']['query'] = kw_string
    query['query']['bool']['must'][0]['query_string']['time_zone'] = tz
    query['query']['bool']['filter'][0]['range']['norm.timestamp']['gte'] = start_time
    query['query']['bool']['filter'][0]['range']['norm.timestamp']['lte'] = end_time

    return query

