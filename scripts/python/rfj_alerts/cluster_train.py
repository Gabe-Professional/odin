import os
import datetime as dt
import matplotlib.pyplot as plt
import odin.utils.munging as oum
import odin.collect.elastic_search as oce
import pandas as pd
import glob
import numpy as np
from sklearn.cluster import KMeans
from sklearn.model_selection import train_test_split
import pickle
import requests as req
import json
from odin.utils.projects import setup_project_directory
from odin.collect.elastic_search import Db, build_body_kw_query, make_pretty_df
from odin.utils.munging import parse_vector_string, label_text_from_dict, make_labeled_df

from odin.utils.munging import REWARD_OFFER_NAMES


### AIRTABLE VARIABLES
AT_CRED_PATH = os.path.expanduser('~/.cred/rfj_alerting_at.json')
with open(AT_CRED_PATH, 'r') as f:
    cred_data = json.load(f)

BASE_ID = cred_data['base_id']
TABLE_NAME = cred_data['table_name']
API_KEY = cred_data['api_key']
END = f'https://api.airtable.com/v0/{BASE_ID}/{TABLE_NAME}'
HEADERS = {'Authorization': f'Bearer {API_KEY}',
           'Content-Type': 'application/json'}

### DIRECTORY VARIABLES
LABEL_DIR = 'reward_offer_names'
MAIN_DIR = os.path.expanduser('~/data/odin')
DATA_DIR = os.path.join(MAIN_DIR, f'rfj_alerting/{LABEL_DIR}/data')
LABELS_DICT = {}
COLUMN_TITLE = 'name_label'

### SCRIPT VARIABLES
res = req.get(url=END, headers=HEADERS)
SUCCESS_DATES = [rec['fields']['query_date'] for rec in res.json()['records']]
ENTRIES = [(rec['fields']['name_label'], rec['fields']['query_date']) for rec in res.json()['records']]

SAMPLE_SIZE = 1000


def run():

    # DEFINE VARIABLES
    PROJECT_DIRECTORY = '~/projects/odin/rfj_alerting_app'

    KEYWORDS = REWARD_OFFER_NAMES
    LABELS_DF = pd.read_csv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
                                         'odin', 'data', 'name_labels.csv'))

    LABELS_DICT = {LABELS_DF.iloc[idx, :]['name']: LABELS_DF.iloc[idx, :]['label'] for idx in range(len(LABELS_DF))}

    DIRS = setup_project_directory(PROJECT_DIRECTORY)
    TRAIN_DATA_PKL = os.path.join(DIRS['data'], 'cluster_train', 'train_data.pkl')
    CLUSTER_PKL_FP = os.path.join(DIRS['data'], 'cluster_train', 'kmeans_model.pkl')

    counts_df = pd.read_pickle(os.path.join(DIRS['data'], 'model','daily_counts.pkl'))
    alert_dates = counts_df.loc[counts_df['alert?'] == 1]['date'].unique().tolist()
    alert_kwds = counts_df.loc[counts_df['alert?'] == 1]['keyword_label'].unique().tolist()

    if not os.path.exists(TRAIN_DATA_PKL):
        # GET THE TRAINING DATA
        st = str(counts_df['date'].tolist()[0]) + 'T00:00:00.000Z'
        et = str(counts_df['date'].tolist()[-1]) + 'T00:00:00.000Z'
        fp = os.path.join(DIRS['data'], f'{st}_{et}_elastic_search.csv')
        if not os.path.exists(fp):
            query = build_body_kw_query(KEYWORDS, start_time=st, end_time=et)
            with Db.Create('PROD') as es:
                count = es.count(query=query, index_pattern='pulse')
                print(f'GETTING ELASTICSEARCH DATA: {count} results between {st} - {et}')
                data = es.query(query=query, index_pattern='pulse')
                results_df = make_pretty_df(data)
                results_df.to_csv(fp, index=False)
                print(f'Saving results to {fp}')
        else:
            results_df = pd.read_csv(fp)

        # DO SOME DATA MANIPULATION
        results_df = results_df.loc[results_df['domain'] != 'twitter.com'].drop_duplicates(subset='uid')
        results_df['ln_body_length'] = np.log(results_df.loc[:, 'body'].apply(lambda x: len(x)))
        results_df = make_labeled_df(results_df, labels_dict=LABELS_DICT)
        results_df['date'] = pd.to_datetime(results_df['timestamp']).dt.date.apply(lambda x: str(x))
        results_df.loc[:, 'encoding'] = results_df['encoding'].apply(lambda x: parse_vector_string(x))
        results_df = results_df.loc[results_df['encoding'].notna()]

        print(results_df.columns)
        sample_df = results_df.loc[(results_df['date'].isin(alert_dates)) &
                                   (results_df['keyword_label'].isin(alert_kwds))].sample(n=SAMPLE_SIZE,
                                                                                          random_state=0)\
            .reset_index(drop=True)
        sample_df.to_csv(os.path.join(DIRS['data'], 'training_sample.csv'), index=False)

        #### DEFINE THE FEATURES FOR CLUSTERING
        X = np.array(sample_df.loc[:, 'encoding'].tolist())
        X = np.reshape(np.sum(X, axis=1), newshape=(X.shape[0], 1))
        X = np.append(X, np.reshape(list(sample_df.loc[:, 'ln_body_length']), newshape=(X.shape[0], 1)), axis=1)
        X = np.append(X, np.reshape(list(np.array(sample_df.index)), newshape=(X.shape[0], 1)), axis=1)

        with open(TRAIN_DATA_PKL, 'wb') as pkl:
            pickle.dump(X, pkl)

    elif os.path.exists(TRAIN_DATA_PKL):
        with open(TRAIN_DATA_PKL, 'rb') as pkl:
            print('loading training features from pkl')
            X = pickle.load(pkl)
    sample_df = pd.read_csv(os.path.join(DIRS['data'], 'cluster_train', 'training_sample.csv'))

    #### TRAIN A CLUSTERING MODEL FOR THE DAYS KEYWORDS ALERTED ON...

    X_train, X_test, train_idx, test_idx = train_test_split(X[:, 0:2], X[:, 2], test_size=.3, shuffle=False)
    f, ax = plt.subplots(figsize=(10, 10))
    plt.scatter(X_train[:, 0], X_train[:, 1])

    Ks = list(range(1, 10))
    km = [KMeans(n_clusters=i, random_state=0) for i in Ks]
    res_data = {}

    f, ax = plt.subplots(figsize=(10, 10))
    for i in range(len(km)):
        clusters = Ks[i]
        km[i].fit(X_train)
        sse = km[i].inertia_
        res_data[clusters] = sse

    centroids = km[1].cluster_centers_
    print('CENTORIDS LOCATED AT: \n', centroids)
    print('SSE RESULTS FOR K CLUSTERS: \n', res_data)
    plt.plot(res_data.keys(), res_data.values())
    plt.title('NUMBER OF CLUSTERS VS. SSE')
    plt.grid()
    plt.xlabel('CLUSTERS')
    plt.ylabel('SSE')
    plt.tight_layout()

    pred = km[1].predict(X_test)

    # todo: Start here
    # todo: need to keep the sample data to load the predictions here...
    pred_df = sample_df.iloc[test_idx]
    pred_df.loc[:, 'CLUSTER'] = pred




    # pred_df[['uid', 'body', 'body_language', f'{COLUMN_TITLE}', 'CLUSTER']].to_csv('test_predictions.csv')
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)

    f, ax = plt.subplots(figsize=(10, 10))
    plt.scatter(X_test[:, 0], X_test[:, 1], c=pred_df['CLUSTER'])

    for i in range(len(centroids)):
        plt.scatter(centroids[i][0], centroids[i][1], c='black')
        plt.annotate(text='CENTROID_{}'.format(i), xy=centroids[i])

    plt.title(f'KMEANS TEST SCATTER WITH CENTROIDS, n={len(test_idx)}')
    plt.xlabel('LABSE SUM')
    plt.ylabel('LN FOLLOWER COUNT')
    plt.grid()
    plt.tight_layout()

    # f.savefig('test_scatter.png')
    #### SAVE THE MODEL AS A PKL
    with open(f'{CLUSTER_PKL_FP}', 'wb') as model_pkl:
        pickle.dump(km[1], model_pkl)

    #### OPEN THE PKL AND TEST SOME DATA
    with open(f'{CLUSTER_PKL_FP}', 'rb') as pkl:
        model = pickle.load(pkl)
        centroids = model.cluster_centers_
        pred = model.predict(X_test)
        pred_df = sample_df.iloc[test_idx]
        pred_df.loc[:, 'CLUSTER'] = pred
        print(pred)

        from scipy.spatial.distance import cdist
        print(np.reshape(np.array(centroids[0]), newshape=(1, 2)))

        args = [cdist(np.reshape(np.array(centroids[idx]), newshape=(1, 2)), X_train).argmin() for idx in range(centroids.shape[0])]

        c_docs = sample_df.iloc[args]
        print(c_docs.body.tolist())

if __name__ == '__main__':
    run()


