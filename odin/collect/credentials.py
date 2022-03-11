import os
import json
import requests as req
from elasticsearch import Elasticsearch


def get_creds(cred_file):
    """A function to get the elastic search creds and return the data.

    :param cred_file:
    :return:
    """
    with open(cred_file, 'r') as f:
        data = json.load(f)
    return data


def make_api_call(creds: dict):

    un = creds['username']
    pw = creds['password']
    ep = creds['endpoint'][8:]

    url = ['https://{}:{}@{}'.format(un, pw, ep)]
    es = Elasticsearch(url)

    # ep = str(ep) + '_count'
    headers = {'Accept': 'application/json', 'Content-type': 'application/json'}
    params = {
        "query": {
            "match": {
                "doc.contact.uuid": "e5da51ce-914c-4275-a1ba-1e2cb838e27d"
            }
        }
    }

    # query = json.dumps(params)

    # res = req.get(url=ep, data=query, auth=(un, pw), headers=headers)
    print(es.search(index='pulse-odin', body=params)['hits']['hits'][0].keys())

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
