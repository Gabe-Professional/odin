import logging
import os
import json
import pandas as pd
import requests as req
from elasticsearch import Elasticsearch

cwd = os.getcwd()


def get_creds():
    """A function to get the elastic search creds and return the data.

    :param cred_file:
    :return:
    """
    cp = os.path.expanduser('~/.cred/odin_es_ro.json')
    with open(cp, 'r') as f:
        data = json.load(f)
    return data


def make_api_call(creds: dict, query, index_pattern: str):
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
    results = es.search(index=index_pattern, body=params, size=10000)
    data = results['hits']['hits'][:]
    return data
# def search(uri, term):
#     query = json.dumps({
#         "query": {
#             "match": {
#                 "doc.contact.uuid": term
#             }
#         }
#     })
#     user = ''
#     pw = ''
#     headers = {'Accept': 'application/json', 'Content-type': 'application/json'}
#     response = requests.get(uri, data=query, headers=headers, auth=(user, pw))
#     results = json.loads(response.text)
#     return results
