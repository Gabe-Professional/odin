import logging
import os
import json
import pandas as pd
import requests as req
from odin.credentials.config import BackboneProperties
from elasticsearch import Elasticsearch
import psycopg2
import warnings
logger = logging.getLogger(__name__)
cwd = os.getcwd()



def get_query_from_path(filepath):
    with open(filepath, 'r') as fp:
        query = json.load(fp)
    return query


def get_creds():
    """A function to get the elastic search ES_CREDS and return the data.

    :param cred_file:
    :return:
    """
    cp = os.path.expanduser('~/.cred/odin_es_ro.json')
    with open(cp, 'r') as f:
        data = json.load(f)
    return data


def make_api_call(creds: dict, query, index_pattern: str, max_hits=10000):
    """
    :param creds:
    :param query:
    :param index_pattern:
    :param max_hits:
    :return: data:
    """
    un = creds['username']
    pw = creds['password']
    ep = creds['endpoint'][8:]
    url = ['https://{}:{}@{}'.format(un, pw, ep)]
    es = Elasticsearch(url)

    if type(query) == str:
        with open(query) as f:
            query = json.load(f)
    elif type(query) == dict:
        query = query

    params = query
    results = es.search(index=index_pattern, body=params, size=max_hits)
    data = results['hits']['hits'][:]
    return data


# todo: use this to create the elastic search data base connection...

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


class Db(object):

    def __init__(self, **connection_args):
        self.logger = logging.getLogger(__name__)

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
            # todo: try to do with with kwargs...
            url = parse_url(username=connection_args['username'],
                            password=connection_args['password'],
                            endpoint=connection_args['endpoint'])
            self._conn = Elasticsearch(url)
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
        logger.info(f'Creating database connection to Elastic {cluster}')
        bp = BackboneProperties()
        connection_info = {}
        for key in ['username', 'password', 'endpoint']:
            try:
                connection_info[key] = bp[f'{cluster}_ELASTIC_{key.upper()}']
            except KeyError:
                warnings.warn(AdminDBWarning(f'Could not load {key} from Credentials. Proceeding...'))
        return Db(**connection_info)

    def query(self, query, index_pattern, batch_size=None, search_after=True):
        """Helper function to query Elasticsearch easily...
        """

        if type(query) == str:
            with open(query) as f:
                query = json.load(f)
        elif type(query) == dict:
            query = query
        # todo: figure out the best way to load the query...either full dsl json or query['query']
        # todo: need to conditionally use search after and batch. If the results are less than the batch
        #  size, the function fails. To avoid, conditionally use batch size based on the count...
        #  if count is less than batch size, simply query as normal...
        
        if search_after:
            if not batch_size:
                logger.info('Setting default batch size to 100...')
                batch_size = 50

            count = self.count(query=query, index_pattern=index_pattern)
            results = self._conn.search(index=index_pattern, query=query['query'], size=batch_size, sort='_id')
            data = results['hits']['hits'][:]
            _id = results['hits']['hits'][batch_size - 1]['_id']
            logging.info('Batching data from Elasticsearch...')
            while count > len(data):
                results = self._conn.search(index=index_pattern, query=query['query'],
                                            size=batch_size, sort='_id', search_after=[_id])
                current_batch = len(results['hits']['hits'][:])
                _id = results['hits']['hits'][current_batch - 1]['_id']
                data += results['hits']['hits'][:]
        else:
            if not batch_size:
                logger.info('Setting batch size to max records...10,000')
                batch_size = 10000
            results = self._conn.search(index=index_pattern, body=query, size=batch_size)
            data = results['hits']['hits'][:]
        return data

    def count(self, query, index_pattern):
        if type(query) == str:
            with open(query) as f:
                query = json.load(f)
        elif type(query) == dict:
            query = query
        res = self._conn.count(index=index_pattern, body=query)
        size = res['count']
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

