import os
import json

import matplotlib.pyplot as plt
import requests as req
import numpy as np
import pandas as pd
import dateutil.parser as date_parser
from datetime import timedelta
import odin.collect.elastic_search as oce
import odin.utils.munging as oum
import pickle
from scipy.spatial.distance import cdist


##### SCRIPT VARIABLES
LOG_HISTORICAL = False
SAVE_CSV = True
LOG_AIRTABLE = True


##### FILE PATH VARIABLES #####
DIRNAME = os.path.dirname(__file__)
# todo: need to make the directories if they don't exist...
LABEL_DIR = 'reward_offer_names'
MAIN_DIR = os.path.expanduser('~/data/odin')
DATA_DIR = os.path.join(MAIN_DIR, f'rfj_alerting/{LABEL_DIR}/data')


DAILY_COUNTS_FP = os.path.realpath(os.path.join(DIRNAME, '../..', '..', '..', 'odin', 'data', 'daily_counts.csv'))
NAME_LABELS_FP = os.path.realpath(os.path.join(DIRNAME, '../..', '..', '..', 'odin', 'data', 'name_labels.csv'))
PLOTS_DIR = os.path.join(MAIN_DIR, f'rfj_alerting/{LABEL_DIR}/plots')
LIMITS_JSON_FP = os.path.realpath(os.path.join(DIRNAME, '../..', '..', '..', 'odin', 'data', 'limits.json'))
PKL_FP = os.path.join(DIRNAME, '../kmeans_model.pkl')

assert os.path.exists(LIMITS_JSON_FP)
assert os.path.exists(DAILY_COUNTS_FP)
assert os.path.exists(PKL_FP)
assert os.path.exists(NAME_LABELS_FP)

##### QUERY VARIABLES
ES_CREDS = oce.get_creds()
QUERY_FP = os.path.join(f'{MAIN_DIR}', 'discover', 'dsl_queries', 'names_query.json')
INDEX_PATTERN = 'pulse'

##### DATA VARIABLES
COLUMN_TITLE = 'name_label'
LABELS_DICT = {}
AT_DATA = {
            "records": [
                {
                    "fields": {
                        "query_date": str(""),
                        "document_count": int(0),
                        "LN_document_count": float(0),
                        f"{COLUMN_TITLE}": str(""),
                        "cluster_center_doc": str(""),
                        "urls": str("")
                    }
                }
            ]
        }


##### AIRTABLE BASE VARIABLES
AT_CRED_PATH = os.path.expanduser('~/.cred/rfj_alerting_at.json')
with open(AT_CRED_PATH, 'r') as f:
    cred_data = json.load(f)

BASE_ID = cred_data['base_id']
TABLE_NAME = cred_data['table_name']
API_KEY = cred_data['api_key']

END = f'https://api.airtable.com/v0/{BASE_ID}/{TABLE_NAME}'
HEADERS = {'Authorization': f'Bearer {API_KEY}',
           'Content-Type': 'application/json'}


tmp = pd.read_csv(NAME_LABELS_FP)
with open(LIMITS_JSON_FP, 'r') as fp:
    limits_dict = json.load(fp=fp)
for idx in range(len(tmp)):
    key, label = tmp.iloc[idx, :]['name'], tmp.iloc[idx, :]['label']
    LABELS_DICT[key] = label


def run():

    # ---------------------------------------------------------------------------- #
    ##### Import the historical daily counts data and limits data #####
    # ---------------------------------------------------------------------------- #


    counts_df = pd.read_csv(filepath_or_buffer=DAILY_COUNTS_FP)

    # ---------------------------------------------------------------------------- #
    ##### log the historical dates #####
    # ---------------------------------------------------------------------------- #
    ## todo: maybe move this to get historical counts...
    if LOG_HISTORICAL is True:
        for idx in range(len(counts_df)):
            name = str(counts_df.iloc[idx][f'{COLUMN_TITLE}'])
            count = int(counts_df.iloc[idx]['count'])
            date = str(counts_df.iloc[idx]['date'])
            limit = limits_dict[name]
            ln_count = np.log(count)

            if ln_count > limit:
                AT_DATA['records'][0]['fields']['query_date'] = date
                AT_DATA['records'][0]['fields']['document_count'] = count
                AT_DATA['records'][0]['fields']['LN_document_count'] = ln_count
                AT_DATA['records'][0]['fields']['name_label'] = name
                res = req.post(url=END, json=AT_DATA, headers=HEADERS)
                print(AT_DATA)

    last_entry_date = max(pd.to_datetime(counts_df['date']))
    query_start_time = str(date_parser.parse(str(last_entry_date + timedelta(days=1))).isoformat(timespec='milliseconds') + 'Z')
    query_end_time = date_parser.parse(str(last_entry_date + timedelta(days=2)))
    query_end_time = query_end_time - timedelta(milliseconds=1)
    query_end_time = str(query_end_time.isoformat(timespec='milliseconds') + 'Z')

    last_entry = str(date_parser.parse(counts_df['date'].iloc[-1]).isoformat(timespec='milliseconds') + 'Z')

    print('LAST ENTRY IN DAILY COUNTS ON ', last_entry)
    print('QUERY START TIME: ', query_start_time)
    print('QUERY END TIME: ', query_end_time)

    # ---------------------------------------------------------------------------- #
    ##### Query ElasticSearch for daily counts #####
    # ---------------------------------------------------------------------------- #
    with open(QUERY_FP, 'r') as qp:
        query = json.load(qp)
        query['query']['bool']['filter'][0]['range']['norm.timestamp']['gte'] = query_start_time
        query['query']['bool']['filter'][0]['range']['norm.timestamp']['lte'] = query_end_time

    query_data = oce.make_api_call(creds=ES_CREDS, query=query, index_pattern=INDEX_PATTERN)
    query_df = oum.clean_data(query_data, drop_duplicate_uids=True)

    # ---------------------------------------------------------------------------- #
    ##### Label the data #####
    # ---------------------------------------------------------------------------- #
    query_df[f'{COLUMN_TITLE}'] = query_df['body'].apply(lambda x: oum.label_text_from_dict(document_text=x, label_dict=LABELS_DICT))
    query_df['date'] = pd.to_datetime(query_df['timestamp'], errors='coerce').dt.date

    #### MAKE A SECOND DATAFRAME WITH MENTIONS OF MULTIPLE RO SUBJECTS
    mult_df = query_df.loc[query_df[f'{COLUMN_TITLE}'].map(len) > 1]
    #### RENAME THE RO SUBJECT AS FIRST ENTRY IN DF AND SECOND ENTRY IN MULT_DF
    query_df[f'{COLUMN_TITLE}'] = query_df.loc[:, f'{COLUMN_TITLE}'].apply(lambda x: x[0] if len(x) > 0 else x)
    #### SAVE THE NEW DATA TO THE DATA DIRECTORY
    if SAVE_CSV:
        query_df.to_csv(path_or_buf=os.path.join(DATA_DIR, f'{query_start_time}_{query_end_time}.csv'), index=False)

    mult_df.loc[:, f'{COLUMN_TITLE}'] = mult_df.loc[:, f'{COLUMN_TITLE}'].apply(lambda x: x[1])
    #### COMBINE THE DATAFRAMES TO GET THE SINGLE RO SUBJECT MENTIONS
    df = pd.concat([query_df, mult_df]).reset_index(drop=True)
    #### GET THE COUNTS OF EACH RO SUBJECTS MENTIONED EACH DAY
    df = df.loc[df.loc[:, f'{COLUMN_TITLE}'].map(len) > 0]

    print('TOTAL DOCUMENTS IN DATASET...', len(df))

    new_counts_df = df.groupby(by=['date', f'{COLUMN_TITLE}'])['uid'].count().reset_index().rename(columns={'uid': 'count'}).sort_values('date')
    total_df = pd.DataFrame(pd.concat([counts_df, new_counts_df]).reset_index(drop=True))
    total_df.loc[:, 'date'] = pd.to_datetime(total_df['date']).dt.date
    total_df = total_df.groupby(by=['date', f'{COLUMN_TITLE}'], axis=0)['count'].sum().reset_index()

    total_df = total_df.sort_values('date').reset_index(drop=True)
    if SAVE_CSV:
        total_df.to_csv(DAILY_COUNTS_FP)

    new_counts_df.loc[:, 'LN_count'] = np.log(new_counts_df['count'])
    print(f'NEW ENTRIES IN COUNTS DF: {len(new_counts_df)}',
          f'TOTAL NEW DOCS ON {query_start_time}:', sum(new_counts_df['count']))

    # ---------------------------------------------------------------------------- #
    ##### Compare daily counts to limits #####
    # ---------------------------------------------------------------------------- #

    docs_df = df.loc[df.loc[:, 'labse_encoding'].map(type) == list].sample(frac=1, random_state=0)
    docs_df['labse_string'] = docs_df['labse_encoding'].apply(lambda x: ''.join(str(a) for a in x))
    docs_df = docs_df.drop_duplicates(subset='labse_string').reset_index(drop=True)
    docs_df = docs_df.dropna(subset=['follower_count'])
    docs_df.loc[:, 'follower_count'] = docs_df.loc[:, 'follower_count'].astype(float).replace(to_replace=0, value=0.0001)
    docs_df.loc[:, 'ln_follower_count'] = np.log(docs_df.loc[:, 'follower_count'])

    cats = list(new_counts_df[f'{COLUMN_TITLE}'].unique())
    for c in cats:
        tmp_docs_df = docs_df.loc[docs_df.loc[:, f'{COLUMN_TITLE}'] == c].reset_index(drop=True)
        tmp = new_counts_df.loc[new_counts_df.loc[:, f'{COLUMN_TITLE}'] == c]
        ln_count = float(tmp['LN_count'])
        count = int(tmp['count'])

        if c in limits_dict:
            limit = limits_dict[c]

            # ---------------------------------------------------------------------------- #
            ##### Log alerting days into airtable and new docs into combined file #####
            # ---------------------------------------------------------------------------- #
            if ln_count >= limit:

                print(f'There may be something happening in the IE regarding {str(c).upper()}...please check...')
                AT_DATA['records'][0]['fields']['query_date'] = query_start_time
                AT_DATA['records'][0]['fields']['document_count'] = count
                AT_DATA['records'][0]['fields']['LN_document_count'] = ln_count
                AT_DATA['records'][0]['fields']['name_label'] = c

                # ---------------------------------------------------------------------------- #
                ##### Run clustering on alert day to see what the breaking news is
                #                                       (return the nearest centroid docs) #####
                # ---------------------------------------------------------------------------- #
                #### OPEN THE PKL AND TEST SOME DATA

                with open(f'{PKL_FP}', 'rb') as pkl:

                    X = np.array(tmp_docs_df.loc[:, 'labse_encoding'].tolist())
                    if X.shape[0] != 0:
                        # print(X)
                        # print(X.shape)
                        # print(df.loc[df.loc[:, f'{COLUMN_TITLE}'] == c])
                        # print(new_counts_df.loc[new_counts_df.loc[:, f'{COLUMN_TITLE}'] == c])
                        X = np.reshape(np.sum(X, axis=1), newshape=(X.shape[0], 1))

                        X = np.append(X, np.reshape(list(tmp_docs_df.loc[:, 'ln_follower_count']), newshape=(X.shape[0], 1)), axis=1)
                        tmp_docs_df['labse_sum'] = X[:, 0]
                        # print('FEATURE DATASET: \n', X)

                        model = pickle.load(pkl)
                        centroids = model.cluster_centers_
                        # print('MODEL CENTROIDS: \n', centroids)

                        pred = model.predict(X)
                        tmp_docs_df.loc[:, 'CLUSTER'] = pred
                        # print('PREDICTED CLUSTERS: \n', pred)

                        args = [cdist(np.reshape(np.array(centroids[idx]), newshape=(1, 2)), X).argmin() for idx in
                                range(centroids.shape[0])]

                        centroid_docs = tmp_docs_df.iloc[args]
                        docs_list = centroid_docs.body.tolist()
                        url_list = centroid_docs.loc[:, 'url'].tolist()
                        print(f'CLOSEST DOCUMENTS TO CENTROID for {c}: \n', docs_list)
                        print(f'CLOSEST URLS TO CENTROID for {c}: \n', url_list)

                        AT_DATA['records'][0]['fields']['cluster_center_doc'] = ', '.join(docs_list)
                        AT_DATA['records'][0]['fields']['urls'] = ', '.join(url_list)


                        f, ax = plt.subplots(figsize=(10, 10))
                        plt.scatter(X[:, 0], X[:, 1], c=pred)
                        for i in range(len(centroids)):
                            plt.scatter(centroids[i][0], centroids[i][1], c='black')
                            plt.annotate(text='CENTROID_{}'.format(i), xy=centroids[i])
                        # todo: add the sample size to the plot title.
                        plt.title(f'CLUSTER RESULTS FOR {c} on {query_start_time}')
                        plt.xlabel('LABSE SUM')
                        plt.ylabel('LN FOLLOWER COUNT')
                        plt.grid()
                        plt.tight_layout()
                        f.savefig(os.path.join(PLOTS_DIR, 'cluster_results', f'{pd.to_datetime(query_start_time).date()}_{c}_predictions.png'))

                    elif X.shape[0] == 0:
                        docs_list = df.loc[df.loc[:, f'{COLUMN_TITLE}'] == c]['body'].tolist()[0:3]
                        url_list = df.loc[df.loc[:, f'{COLUMN_TITLE}'] == c]['url'].tolist()[0:3]
                        print(f'EXAMPLE DOCS FOR {c}: \n', docs_list)
                        print(f'EXAMPLE URLS FOR {c}: \n', url_list)
                        AT_DATA['records'][0]['fields']['cluster_center_doc'] = ', '.join(docs_list)
                        AT_DATA['records'][0]['fields']['urls'] = ', '.join(url_list)

                    if LOG_AIRTABLE:
                        res = req.post(url=END, json=AT_DATA, headers=HEADERS)
                        print(res)

            elif ln_count < limit:
                print(f'There was not a significant increase in traffic for {str(c).upper()}')
            else:
                print(f'something wrong happened...{limit}')
        else:
            print(f'add {c} to limits dict')


if __name__ == '__main__':
    run()
