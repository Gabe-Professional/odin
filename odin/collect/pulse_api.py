import logging
import warnings
import requests
import pandas as pd
import functools
import time
import sys
from multiprocessing.pool import ThreadPool
from odin.credentials.config import BackboneProperties
logger = logging.getLogger(__name__)


class AdminApiError(Exception):
    pass


class AdminApiWarning(UserWarning):
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


class Api(object):

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

        self._conn = connection_args
        # try:
        #     self._conn = requests.connect(**connection_args)
        # except Exception:
        #     msg = 'Connection to DB failed...ensure you have proper credentials and are on VPN'
        #     self.logger.error(msg)
        #     raise AdminDbError(msg)

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
        for key in ['endpoint', 'backend', 'key']:
            try:
                if key == 'backend':
                    connection_info['x-' + key] = bp[f'{cluster}_X_{key.upper()}']
                elif key == 'key':
                    connection_info['x-api-' + key] = bp[f'{cluster}_X_{key.upper()}']
                else:
                    connection_info[key] = bp[f'{cluster}_X_{key.upper()}']
            except KeyError:
                warnings.warn(AdminApiWarning(f'Could not load {key} from Credentials. Proceeding...'))
        return Api(**connection_info)

    def get_headers(self):
        headers = {a: b for a, b in zip(self._conn.keys(), self._conn.values()) if a != 'endpoint'}
        return headers

    def get_endpoint(self):
        endpoint = {a: b for a, b in zip(self._conn.keys(), self._conn.values()) if a == 'endpoint'}['endpoint']
        return endpoint

    def handle_response(self, response):
        if response.status_code == 200:
            return response.json()['data']['encoding']
        elif response.status_code == 400:
            self.logger.warning("Bad Request: Check your request parameters.")
        elif response.status_code == 401:
            self.logger.warning("Unauthorized: Check your API key or authentication credentials.")
        elif response.status_code == 403:
            self.logger.warning("Forbidden: You don't have permission to access this resource.")
        elif response.status_code == 404:
            self.logger.warning("Not Found: The requested resource could not be found.")
        elif response.status_code == 500:
            self.logger.warning("Internal Server Error: The server encountered an unexpected condition.")
        else:
            self.logger.warning(f"Unhandled Status Code: {response.status_code}")
        return None

    # todo: make better way to apply progress bar.
    # @progress_bar
    def make_request(self, text: str, method: str):
        headers = self.get_headers()
        endpoint = self.get_endpoint()
        msg = f'Running {method.upper()} on Data API'
        methods = ['GET', 'POST']
        text_data = {'text': text}
        res = None
        if method.upper() == 'POST':
            res = requests.post(url=endpoint, json=text_data, headers=headers)
            self.logger.info(msg=msg)
        elif method.upper() == 'GET':
            res = requests.get(url=endpoint, json=text_data, headers=headers)
            self.logger.info(msg=msg)
        else:
            self.logger.warning(f'Please provide a valid method for the request {", ".join(methods)}')

        encoding = self.handle_response(res)
        return encoding
