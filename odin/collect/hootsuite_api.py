import json
import os


def get_creds():
    """A function to get the elastic search ES_CREDS and return the data.

    :param cred_file:
    :return:
    """
    cp = os.path.expanduser('~/.cred/hootsuite_api.json')
    with open(cp, 'r') as f:
        data = json.load(f)
    return data