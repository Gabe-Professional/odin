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
PKL_FP = 'kmeans_model.pkl'
SAMPLE_SIZE = 1000


def run():
    tmp = pd.read_csv(os.path.join(DATA_DIR, 'labels', 'name_labels.csv'))

    for idx in range(len(tmp)):
        key, label = tmp.iloc[idx, :]['name'], tmp.iloc[idx, :]['label']
        LABELS_DICT[key] = label

    files = [f for f in glob.glob(os.path.join(DATA_DIR, '*.csv')) if 'daily_counts' not in f]

    print('READING THE FILES TO TRAIN ON...')
    df = pd.concat(map(pd.read_csv, files)).drop_duplicates(subset=['uid', 'timestamp']).reset_index(drop=True)
    df[f'{COLUMN_TITLE}'] = df['body'].apply(lambda x: oum.label_text_from_dict(document_text=x, label_dict=LABELS_DICT))

    #### MAKE A SECOND DATAFRAME WITH MENTIONS OF MULTIPLE RO SUBJECTS
    mult_df = df.loc[df[f'{COLUMN_TITLE}'].map(len) > 1]

    #### RENAME THE RO SUBJECT AS FIRST ENTRY IN DF AND SECOND ENTRY IN MULT_DF
    df[f'{COLUMN_TITLE}'] = df.loc[:, f'{COLUMN_TITLE}'].apply(lambda x: x[0] if len(x) > 0 else x)
    mult_df.loc[:, f'{COLUMN_TITLE}'] = mult_df.loc[:, f'{COLUMN_TITLE}'].apply(lambda x: x[1])

    #### COMBINE THE DATAFRAMES TO GET THE SINGLE RO SUBJECT MENTIONS
    df = pd.concat([df, mult_df]).reset_index(drop=True)
    df['date'] = pd.to_datetime(df['timestamp'], errors='coerce').dt.date

    dates = pd.to_datetime(list(zip(*ENTRIES))[1]).date
    labels = list(zip(*ENTRIES))[0]

    #### MAKE THE LABSE TRAINING DATASET
    df = df.loc[df[f'{COLUMN_TITLE}'].map(len) > 0]
    sample_df = df.loc[(df.loc[:, 'date'].isin(dates)) & (df.loc[:, f'{COLUMN_TITLE}'].isin(labels))]
    sample_df = sample_df.drop_duplicates(subset='labse_encoding').reset_index(drop=True)

    sample_df.loc[:, 'labse_encoding'] = sample_df.loc[:, 'labse_encoding'].apply(lambda x: oum.parse_vector_string(x))
    sample_df = sample_df.dropna(subset=['follower_count'])
    # sample_df.loc[:, 'follower_count'] = sample_df.loc[:, 'follower_count'].astype(float).replace(to_replace=0, value=0.0001)
    sample_df = sample_df.loc[sample_df.loc[:, 'follower_count'] > 0]
    sample_df = sample_df.loc[sample_df.loc[:, 'labse_encoding'].map(type) == list].sample(n=SAMPLE_SIZE, random_state=0).reset_index(drop=True)

    sample_df.loc[:, 'follower_count'] = np.log(sample_df.loc[:, 'follower_count'])
    print(sample_df.head(10))
    print('TOTAL DATA POINTS TO TRAIN ON: ', len(sample_df), len(df))

    #### GET THE FEATURES
    X = np.array(sample_df.loc[:, 'labse_encoding'].tolist())
    X = np.reshape(np.sum(X, axis=1), newshape=(X.shape[0], 1))
    X = np.append(X, np.reshape(list(sample_df.loc[:, 'follower_count']), newshape=(X.shape[0], 1)), axis=1)

    sample_df['labse_sum'] = X[:, 0]
    sample_df['ln_follower_count'] = X[:, 1]

    idx = np.array(sample_df.index.tolist())
    print('THE SHAPE OF THE DATA SET IS: ', X.shape)

    X_train, X_test, train_idx, test_idx = train_test_split(X, idx, test_size=.3, shuffle=False)

    f, ax = plt.subplots(figsize=(10, 10))
    plt.scatter(X_train[:, 0], X_train[:, 1])
    plt.title(f'TRAINING DATA SCATTER (TWITTER ONLY), n={len(train_idx)}')
    plt.xlabel('LABSE SUM')
    plt.ylabel('LN FOLLOWER COUNT')
    plt.grid()
    plt.tight_layout()
    f.savefig('training_scatter.png')

    Ks = list(range(1, 10))
    km = [KMeans(n_clusters=i, random_state=0) for i in Ks]

    res_data = {}

    f, ax = plt.subplots(figsize=(10, 10))
    for i in range(len(km)):
        clusters = Ks[i]
        km[i].fit(X_train)
        sse = km[i].inertia_
        res_data[clusters] = sse

    centroids = km[2].cluster_centers_
    print('CENTORIDS LOCATED AT: \n', centroids)
    print('SSE RESULTS FOR K CLUSTERS: \n', res_data)
    plt.plot(res_data.keys(), res_data.values())
    plt.title('NUMBER OF CLUSTERS VS. SSE (TWITTER ONLY)')
    plt.grid()
    plt.xlabel('CLUSTERS')
    plt.ylabel('SSE')
    plt.tight_layout()
    f.savefig('elbow_method_training_results.png')
    pred = km[2].predict(X_test)

    pred_df = sample_df.iloc[test_idx]
    pred_df.loc[:, 'cluster'] = pred

    pred_df[['uid', 'body', 'body_language', f'{COLUMN_TITLE}', 'cluster']].to_csv('test_predictions.csv')
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)

    f, ax = plt.subplots(figsize=(10, 10))
    plt.scatter(X_test[:, 0], X_test[:, 1], c=pred_df['cluster'])
    for i in range(len(centroids)):
        plt.scatter(centroids[i][0], centroids[i][1], c='black')
        plt.annotate(text='CENTROID_{}'.format(i), xy=centroids[i])

    plt.title(f'KMEANS TEST SCATTER WITH CENTROIDS, n={len(test_idx)}')
    plt.xlabel('LABSE SUM')
    plt.ylabel('LN FOLLOWER COUNT')
    plt.grid()
    plt.tight_layout()

    f.savefig('test_scatter.png')
    #### SAVE THE MODEL AS A PKL
    with open(f'{PKL_FP}', 'wb') as model_pkl:
        pickle.dump(km[2], model_pkl)

    #### OPEN THE PKL AND TEST SOME DATA
    with open(f'{PKL_FP}', 'rb') as pkl:
        model = pickle.load(pkl)
        centroids = model.cluster_centers_
        pred = model.predict(X_test)
        pred_df = sample_df.iloc[test_idx]
        pred_df.loc[:, 'cluster'] = pred
        print(pred)

        from scipy.spatial.distance import cdist
        print(np.reshape(np.array(centroids[0]), newshape=(1, 2)))

        args = [cdist(np.reshape(np.array(centroids[idx]), newshape=(1, 2)), X_train).argmin() for idx in range(centroids.shape[0])]
        c_docs = sample_df.iloc[args]
        print(c_docs.body.tolist())


if __name__ == '__main__':
    run()
