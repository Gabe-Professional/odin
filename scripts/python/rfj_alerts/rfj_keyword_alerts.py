import datetime
from datetime import timedelta
import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import requests
import pickle
from odin.utils.munging import REWARD_OFFER_NAMES
from odin.utils.airtable import make_records_dict, get_alerting_creds
from odin.utils.munging import parse_vector_string, make_labeled_df
from odin.collect.elastic_search import Db, build_body_kw_query, make_pretty_df
from odin.utils.projects import setup_project_directory
import scipy.stats as stats
from scipy.spatial.distance import cdist



# THIS SCRIPT SHOULD
# 1. TAKE A LIST OF DESIRED KEYWORDS AS AN INPUT
# 2. QUERY ELASTIC SEARCH FOR A 30 DAY PERIOD
# 3. ASSESS THE FREQUENCIES OF THE USER INPUT KEYWORDS
# 4. DEFINE THE CONFIDENCE INTERVAL FOR EACH KEYWORD
# 5. LOG THE INTERVALS FOR EACH KEYWORD

# THE SCRIPT SHOULD BE ABLE TO BE RUN ON A DAILY FREQUENCY FOR A SET OF KEYWORDS AND UPDATE THE CONFIDENCE INTERVAL
# FOR A ROLLING 30 DAY INTERVAL
#
# RUNNING THIS PROGRAM DOES HAS SOME LIMITS. ELASTICSEARCH API SEEMS TO LIMIT RESULTS TO 10K.
# WE COULD GET AROUND THIS BY QUERYING A SMALLER TIME FRAME REPEATEDLY. USING POPULAR KEYWORD SUCH AS BIDEN,
# YIELDS LOTS OF RESULTS.


# START WITH 30 DAYS OF DATA FOR EACH KEYWORD.
# QUERY EACH DAY AND UPDATE THE COUNTS DATA SET WITH THE CURRENT DAYS COUNT
# RE-EVALUATE THE LIMITS OF EACH KEYWORD. USE SAMPLE OF 30 DAYS FOR EACH KEYWORD...


# todo: make some variables to ingest with args from CLI...may need to move scripts to 'odin' level...
# todo: need an easy way to add new keywords and their labels.
# todo: need an easy way to add custom keywords list...not priority, this would be for other pulse users/analysts...

# todo: make this part of the CLI... odin alerting [ARGS...]


def conf_intervals_from_category(df: pd.DataFrame, value, log=True):
    col = 'keyword_label'

    if log:
        tmp = df.loc[(df[col] == value) & (df['count'] > 0)]
        mu = np.log(tmp['count']).mean()
    else:
        tmp = df.loc[df[col] == value]
        mu = tmp['count'].mean()

    if len(tmp) >= 30:
        conf = stats.t.interval(alpha=.95, df=len(tmp) - 1, loc=mu)
    else:
        conf = (float, float)

    return conf


def log_daily_counts(project_dirs: dict, fname, keywords: list, labels_dict: dict):
    counts_pkl = os.path.join(project_dirs['data'], 'daily_counts.pkl')

    end = pd.to_datetime(str(datetime.datetime.now().date())) + timedelta(seconds=-1)
    et = end.isoformat() + str('.999Z')
    get_data = False

    if os.path.exists(counts_pkl):
        df = pd.read_pickle(counts_pkl)
        last = df['date'].tolist()[-1]

        if last != end.date():
            st = str((last + timedelta(days=1))) + str('T00:00:00.000Z')
            get_data = True
        else:
            st = last.isoformat() + str('T00:00:00.000Z')
            print(f'{fname} is up to date!! Latest date logged: {last}')
    else:
        df = pd.DataFrame()
        get_data = True
        st = end + timedelta(days=-100)
        et = (end + timedelta(seconds=-1)).isoformat() + str('.999Z')

    if get_data:
        if len(keywords) != 0:

            query = build_body_kw_query(keywords=keywords, start_time=st, end_time=et)
            with Db.Create('PROD') as es:

                count = es.count(query=query, index_pattern='pulse')
                print(f'GETTING ELASTICSEARCH DATA: {count} results between {st} - {et}')
                data = es.query(index_pattern='pulse', query=query)

                tmp = make_pretty_df(data)

            tmp = make_labeled_df(tmp, labels_dict=labels_dict)

            pd.set_option('display.max_columns', None)
            tmp['date'] = pd.to_datetime(tmp['timestamp'], format='mixed').dt.date

            # counts = tmp.groupby(by=['date',
            #                          'keyword_label']).uid.count().reset_index().rename(
            #     columns={'uid': 'count'}).sort_values('date')

            # todo: sum the vector here...no reason to have to do it later...
            # todo: also can get the body length here...
            counts = tmp.groupby(by=[
                'date',
                'keyword_label']).agg({'uid': 'count',
                                       'encoding': lambda x: [sum(a) if a is not None else 0 for a in x],
                                       'body': lambda x: list(x),
                                       'url': lambda x: list(x)}).reset_index().rename(columns={'uid': 'count'})

            df = pd.DataFrame(pd.concat([df, counts]).reset_index(drop=True))
            df.to_pickle(counts_pkl)

    return df, st, et


def make_conf_dict(counts_df: pd.DataFrame, project_dirs, plot=False):
    labels = list(counts_df['keyword_label'].unique())
    conf_dict = {}
    size = 30
    if plot:
        print(f'Making plots for keywords and saving to {project_dirs["plots"]}')

    for lab in labels:
        tmp = pd.DataFrame(counts_df.loc[(counts_df['keyword_label'] == lab) & (counts_df['count'] > 0)])
        if len(tmp) >= size:
            tmp = tmp.sample(n=size, random_state=1)
            log_count = np.log(tmp['count'])
            dates = tmp['date']
            mu = np.mean(log_count)

            conf = stats.t.interval(confidence=.95, df=len(log_count) - 1, loc=mu)
            conf_dict[lab] = conf

            if plot:
                # MAKE HISTOGRAM, PROBABILITY PLOT, TIME SERIES
                f, ax = plt.subplots(nrows=3, figsize=(10, 10))
                h = ax[0].hist(log_count, ec='w')
                y_lim = h[0].max()
                ax[0].axvline(x=conf[0], color='black')
                ax[0].axvline(x=conf[1], color='black')
                ax[0].axvline(x=mu.round(decimals=3), color='black')
                ax[0].annotate(text=mu.round(3), xy=(mu, y_lim - 1))
                ax[0].annotate(text=conf[0].round(3), xy=(conf[0], y_lim - 1))
                ax[0].annotate(text=conf[1].round(3), xy=(conf[1], y_lim - 1))
                ax[0].set_title(f'\n n: {len(tmp)}, Keyword: {lab}')
                ax[0].set_xlabel('LN daily count')

                p = stats.probplot(x=log_count, dist='norm', plot=ax[1])
                rsq = round(p[1][2], 4)

                ax[1].set_title('Probability Plot \n R^2: {}'.format(rsq))
                ax[2].scatter(x=pd.to_datetime(dates), y=log_count)
                ax[2].axhline(y=conf[0], color='black', ls='dashed')
                ax[2].axhline(y=conf[1], color='black', ls='dashed')
                ax[2].axhline(y=mu, color='black', ls='dashed')
                ax[2].set_ylabel('LN Daily Count')
                ax[2].grid()
                plt.xticks(rotation=45, ha='right')

                plt.tight_layout()

                fp = os.path.join(project_dirs['plots'], f'{lab}.png')
                f.savefig(fp)
        else:
            conf_dict[lab] = (float, float)

    return conf_dict


def assess_freq(label, count, conf_dict):
    ln_count = np.log(count)
    high = conf_dict[label][1]
    # todo: could do a try statement here instead...
    if not isinstance(high, type):
        if ln_count >= high:
            alert = 1
        else:
            alert = 0
    else:
        alert = 0
    return alert


def show_results(row):
    date = row['date']
    keyword_label = row['keyword_label']
    alert = row['alert?']
    if alert == 1:
        print(f'A significant increase in ELASTICSEARCH traffic discussing {keyword_label} occurred on {date}')
    else:
        print(f'Nothing to report from ELASTICSEARCH traffic regarding {keyword_label} occurred on {date}')


def log_at_results(result):
    at_cols = ['query_date', "document_count", "LN_document_count", "name_label", "cluster_center_doc", "urls"]
    count = result['document_count']
    ln_count = np.log(count)
    label = result['name_label']
    date = result['query_date']
    urls = result['urls']
    alert = result['alert?']
    center_doc = result['cluster_center_docs']
    at_records_dict = make_records_dict(at_cols)
    at_creds = get_alerting_creds()
    end_point = f'{at_creds["url"]}{at_creds["base_id"]}/{at_creds["table_names"][0]}'

    headers = {'Authorization': f'Bearer {at_creds["api_key"]}',
               'Content-Type': 'application/json'}
    at_records_dict['records'][0]['fields']['query_date'] = date
    at_records_dict['records'][0]['fields']['document_count'] = count
    at_records_dict['records'][0]['fields']['LN_document_count'] = ln_count
    at_records_dict['records'][0]['fields']['name_label'] = label
    at_records_dict['records'][0]['fields']['cluster_center_doc'] = center_doc
    at_records_dict['records'][0]['fields']['urls'] = urls
    res = requests.post(url=end_point, json=at_records_dict, headers=headers)
    print('AIRTABLE STATUS CODE:', res.status_code)


def main():

    # MAIN VARIABLES
    KEYWORDS = REWARD_OFFER_NAMES
    PROJECT_DIRECTORY = '~/projects/odin/rfj_alerting_app'
    project_dirs = setup_project_directory(PROJECT_DIRECTORY)

    LABELS_DF = pd.read_csv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
                                         'odin', 'data', 'name_labels.csv'))

    LABELS_DICT = {LABELS_DF.iloc[idx, :]['name']: LABELS_DF.iloc[idx, :]['label'] for idx in range(len(LABELS_DF))}
    NEW_DATE = (datetime.datetime.now() + timedelta(days=-1)).date()
    PLOT = False

    counts_df, st, et = log_daily_counts(project_dirs=project_dirs,
                                         fname='daily_counts.csv',
                                         keywords=KEYWORDS,
                                         labels_dict=LABELS_DICT)
    pd.set_option('display.max_columns', None)

    # MAKE A LIST OF DATES TO LOG GREATER THAN OR EQUAL TO THE START QUERY TIME
    log_dates = pd.to_datetime(counts_df['date']).dt.date
    log_dates = [str(d) for d in log_dates.loc[log_dates >= pd.to_datetime(st).date()].unique().tolist()]

    # MAKE THE CONFIDENCE INTERVALS...SAMPLE THE COUNTS DATA FOR 30 DAYS OF EACH KEYWORD...AS TIME GOES ON,
    conf_dict = make_conf_dict(counts_df, project_dirs=project_dirs, plot=PLOT)

    ## ASSESS THE FREQUENCIES OF NEW DOCUMENT COUNTS (YESTERDAY)
    counts_df.loc[:, 'alert?'] = counts_df.apply(lambda row: assess_freq(row['keyword_label'],
                                                                         row['count'], conf_dict=conf_dict), axis=1)
    counts_df = counts_df.sort_values(by=['date', 'keyword_label'])

    counts_df.to_pickle(os.path.join(project_dirs['data'], 'daily_counts.pkl'))

    tmp = pd.DataFrame(counts_df.loc[(counts_df['date'].isin(log_dates)) |
                                     (counts_df['date'].isin(pd.to_datetime(log_dates).date))])

    # LOG ALERTING RESULTS INTO AIRTABLE
    pd.set_option('display.max_columns', None)
    tmp['body_length'] = tmp['body'].apply(lambda x: [len(a) if a is not None else 0 for a in x])

    if len(tmp.loc[tmp['alert?'] == 1]) != 0:

        for row in range(len(tmp)):
            data = {'document_count': [tmp.iloc[row]['count']],
                    'query_date': [str(tmp.iloc[row]['date'])],
                    'alert?': [tmp.iloc[row]['alert?']],
                    'LN_document_count': [np.log(tmp.iloc[row]['count'])],
                    'name_label': [tmp.iloc[row]['keyword_label']],
                    'urls': [],
                    'cluster_center_docs': []}

            X = np.array(tmp.iloc[row]['encoding'])
            X = np.reshape(X, newshape=(X.shape[0], 1))

            ln_body_len = np.reshape(np.array(np.log(tmp.iloc[row]['body_length'])), newshape=(X.shape[0], 1))
            body = tmp.iloc[row]['body']
            url = tmp.iloc[row]['url']

            X = np.append(X, ln_body_len, axis=1)

            with open(os.path.join(project_dirs['data'], 'kmeans_model.pkl'), 'rb') as pkl:
                model = pickle.load(pkl)
                centroids = model.cluster_centers_
                pred = np.reshape(np.array(model.predict(X)), newshape=(X.shape[0], 1))

            X = np.append(X, pred, axis=1)
            args = [cdist(np.reshape(np.array(centroids[idx]), newshape=(1, 2)), X[:, 0:2]).argmin() for idx in
                    range(centroids.shape[0])]
            docs = [body[idx] for idx in args]
            urls = [url[idx] for idx in args]
            data['cluster_center_docs'].append(', '.join(docs))
            data['urls'].append(', '.join(urls))
            log_df = pd.DataFrame(data)

            f, ax = plt.subplots(figsize=(10, 10))
            plt.scatter(X[:, 0], X[:, 1], c=X[:, 2])
            plt.scatter(centroids[:, 0], centroids[:, 1], c='black')
            if len(log_df.loc[log_df['alert?'] == 1]) > 0:
                print(log_df.loc[log_df['alert?'] == 1])
            log_df.loc[log_df['alert?'] == 1].apply(lambda res: log_at_results(res), axis=1)
    else:
        print(f'NO RECORDS TO LOG IN AT. {len(tmp)} keywords added to daily counts for {NEW_DATE}')

    # todo: retrain the clustering model using the daily_counts.pkl...instead of downloading the data again...
    print('Number of days alerted with RFJ keywords:', len(counts_df.loc[counts_df['alert?'] == 1]))


if __name__ == '__main__':
    main()
