import os
import json
import requests


def get_creds(cred_file):
    """A function to get the elastic search creds and return the data.

    :param cred_file:
    :return:
    """
    with open(cred_file, 'r') as f:
        data = json.load(f)
    return data


def build_api_call(data: dict):
    un = data['username']
    pw = data['password']
    ep = data['endpoint']
    print(un, pw, ep)
