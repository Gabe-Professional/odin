import json
import os

import numpy as np
import pandas as pd


def clean_data(data):

    tmp = {'uid': [],
           'timestamp': [],
           'system_timestamp': [],
           'author': [],
           'body': [],
           'body_language': [],
           'domain': [],
           'labse_encoding': [],
           'body_translation': [],
           'follower_count': []
           }

    for res in data:

        try:
            uid = res['_source']['uid']
        except:
            uid = None
        try:
            auth = res['_source']['norm']['author']
        except:
            auth = None
        try:
            txt = res['_source']['norm']['body']
        except:
            txt = None
        try:
            bl = res['_source']['meta']['body_language'][0]['results'][0]['value']
        except:
            bl = None
        try:
            dom = res['_source']['norm']['domain']
        except:
            dom = None
        try:
            ts = pd.to_datetime(res['_source']['norm']['timestamp'])
        except:
            ts = None
        try:
            sts = pd.to_datetime(res['_source']['system_timestamp'])
        except:
            sts = None
        try:
            en = res['_source']['meta']['ml_labse'][0]['results'][0]['encoding']
        except:
            en = None
        try:
            bt = str(res['_source']['meta']['ml_translate'][0]['results'][0]['text'])
        except:
            bt = None
        try:
            fc = int(res['_source']['meta']['followers_count'][0]['results'][0])
        except:
            fc = None

        tmp['uid'].append(uid)
        tmp['timestamp'].append(ts)
        tmp['system_timestamp'].append(sts)
        tmp['author'].append(auth)
        tmp['body'].append(txt)
        tmp['body_language'].append(bl)
        tmp['domain'].append(dom)
        tmp['labse_encoding'].append(en)
        tmp['body_translation'].append(bt)
        tmp['follower_count'].append(fc)

    pd.set_option('display.max_columns', None)
    df = pd.DataFrame(tmp).drop_duplicates(subset='uid').sort_values(by='system_timestamp')
    return df


# todo: need a function here to input a custom datetime and tz to the .json query
def change_query_datetime(start_time, end_time, query_path):
    with open(query_path) as qp:
        data = json.load(qp)
        data['query']['bool']['filter'][3]['range']['system_timestamp']['gte'] = start_time
        data['query']['bool']['filter'][3]['range']['system_timestamp']['lte'] = end_time
    return data


def parse_vector_string(vector_string):
    try:
        vl = vector_string.replace('[', '').replace(']', '').replace(',', '').split()
        vl = [float(i) for i in vl]
    except:
        vl = None
    return vl


