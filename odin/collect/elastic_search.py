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


def make_api_call(creds: dict, query_file_path, index_pattern: str):

    un = creds['username']
    pw = creds['password']
    ep = creds['endpoint'][8:]
    url = ['https://{}:{}@{}'.format(un, pw, ep)]
    es = Elasticsearch(url)

    # ep = str(ep) + '_count'
    headers = {'Accept': 'application/json', 'Content-type': 'application/json'}

    with open(query_file_path) as f:
        query = json.load(f)

    params = query

    # res = req.get(url=ep, data=query, auth=(un, pw), headers=headers)
    results = es.search(index=index_pattern, body=params, size=10000)
    data = results['hits']['hits'][:]
    print(data[0]['_source'].keys())
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
