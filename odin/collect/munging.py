import json
import os
import pandas as pd


def clean_data(data):

    tmp = {'uid': [],
           'timestamp': [],
           'system_timestamp': [],
           'author': [],
           'body': [],
           'body_language': [],
           'domain': [],
           'labse_encoding': []
           }

    # todo: need to fix...data not looking right...
    for res in data:
        uid = res['_source']['uid']
        auth = res['_source']['norm']['author']
        txt = res['_source']['norm']['body']
        try:
            bl = res['_source']['meta']['body_language'][0]['results'][0]['value']
            dom = res['_source']['norm']['domain']
            ts = pd.to_datetime(res['_source']['norm']['timestamp'])
            sts = pd.to_datetime(res['_source']['system_timestamp'])
            en = res['_source']['meta']['ml_labse'][0]['results'][0]['encoding']

        except:
            bl = None
            dom = None
            ts = None
            sts = None
            en = None

        tmp['uid'].append(uid)
        tmp['timestamp'].append(ts)
        tmp['system_timestamp'].append(sts)
        tmp['author'].append(auth)
        tmp['body'].append(txt)
        tmp['body_language'].append(bl)
        tmp['domain'].append(dom)
        tmp['labse_encoding'].append(en)

    pd.set_option('display.max_columns', None)
    df = pd.DataFrame(tmp).drop_duplicates(subset='uid').sort_values(by='system_timestamp')
    print(df)
    return df


# todo: need a function here to input a custom datetime and tz to the .json query
def change_query_datetime(start_time, end_time, query_path):
    print(start_time, end_time, query_path)
    with open(query_path) as qp:
        data = json.load(qp)
        data['query']['bool']['filter'][3]['range']['system_timestamp']['gte'] = start_time
        data['query']['bool']['filter'][3]['range']['system_timestamp']['lte'] = end_time
    return data

