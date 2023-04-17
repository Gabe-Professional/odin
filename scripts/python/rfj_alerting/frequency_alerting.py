import datetime
from datetime import timedelta
import os
import csv
import numpy as np
import pandas as pd
from odin.utils.munging import REWARD_OFFER_NAMES
from odin.utils.munging import parse_vector_string, label_text_from_dict
from odin.collect.elastic_search import Db, build_body_kw_query, make_pretty_df
from odin.utils.projects import setup_project_directory
import scipy.stats as stats
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

KEYWORDS = REWARD_OFFER_NAMES
# KEYWORDS = ['biden', 'nato']

LABELS_DF = pd.read_csv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
                                     'odin', 'data', 'name_labels.csv'))
LABELS_DICT = {LABELS_DF.iloc[idx, :]['name']: LABELS_DF.iloc[idx, :]['label'] for idx in range(len(LABELS_DF))}
PROJECT_DIRECTORY = '~/projects/odin/rfj_alerting_app'

NEW_DATE = (datetime.datetime.now() + timedelta(days=-1)).date()
END_DATE = (datetime.datetime.now() + timedelta(days=-2)).date()
START_DATE = END_DATE + timedelta(days=-30)
INDEX_PATTERN = 'pulse'
CLUSTER = 'PROD'

# todo: make this part of the CLI... odin alerting [ARGS...]


def conf_intervals_from_category(df: pd.DataFrame, value, log=True):
    col = 'keyword_label'

    if log:
        tmp = df.loc[(df[col] == value) & (df['count'] > 0)]
        mu = np.log10(tmp['count']).mean()
    else:
        tmp = df.loc[df[col] == value]
        mu = tmp['count'].mean()

    if len(tmp) >= 30:
        conf = stats.t.interval(alpha=.95, df=len(tmp) - 1, loc=mu)
    else:
        conf = (float, float)

    return conf


def log_daily_counts(project_dirs: dict, fname, keywords: list, labels_dict: dict):
    daily_counts = os.path.join(project_dirs['data'], fname)
    end = pd.to_datetime(str((datetime.datetime.now() + timedelta(days=-1)).date()))
    df = pd.read_csv(daily_counts)
    get_data = False
    last = str
    first = str

    if os.path.exists(daily_counts):
        with open(daily_counts, 'r') as f:
            lines = f.readlines()
            first = pd.to_datetime(lines[1].split(sep=',')[1])
            last = pd.to_datetime(lines[-1].split(',')[1])
            if last != end:
                get_data = True
    else:
        get_data = True

    if get_data:
        if len(keywords) != 0:
            st = str(last.date()) + str('T00:00:00.000Z')
            et = str(end.date()) + str('T00:00:00.000Z')
            print(st, et)
            query = build_body_kw_query(keywords=keywords, start_time=st, end_time=et)
            with Db.Create('PROD') as es:
                data = es.query(index_pattern='pulse', query=query)
                tmp = make_pretty_df(data)
            tmp['keyword_label'] = tmp['body'].apply(lambda x: label_text_from_dict(document_text=x, label_dict=labels_dict))
            mult_df = tmp.loc[tmp['keyword_label'].map(len) > 1]
            mult_df.loc[:, 'keyword_label'] = mult_df.loc[:, 'keyword_label'].apply(lambda x: x[1])
            tmp.loc[:, 'keyword_label'] = tmp.loc[:, 'keyword_label'].apply(lambda x: x[0] if len(x) != 0 else None)

            
            counts = pd.DataFrame(pd.concat([tmp, mult_df])).reset_index(drop=True)
            print(counts)









def main():
    project_dirs = setup_project_directory(PROJECT_DIRECTORY)

    log_daily_counts(project_dirs=project_dirs, fname='daily_counts.csv', keywords=KEYWORDS, labels_dict=LABELS_DICT)

    exit()
    # QUERY ELASTIC SEARCH FOR THE DESIRED KEYWORDS
    st = str(START_DATE) + str('T00:00:00.000Z')
    et = str(END_DATE) + str('T00:00:00.000Z')
    nst = str(NEW_DATE) + str('T00:00:00.000Z')
    net = str(NEW_DATE + timedelta(days=1)) + str('T00:00:00.000Z')

    # print(os.(os.path.expanduser(PROJECT_DIRECTORY)))
    # exit()


    query = build_body_kw_query(keywords=KEYWORDS, start_time=st, end_time=et)

    results_fp = os.path.join(project_dirs['data'], f'{st}_{et}_historical_keyword_results.csv')
    if os.path.exists(results_fp):
        df = pd.read_csv(results_fp)
        # todo: query for just the previous day, resave the file with still only previous 30 days...

    else:
        with Db.Create(CLUSTER) as es:
            size = es.count(index_pattern=INDEX_PATTERN, query=query)
            print('TOTAL COUNT FOR ES QUERY: ', size)
            data = es.query(query=query, index_pattern=INDEX_PATTERN)
            df = make_pretty_df(data)
            print('TOTAL DATA POINTS RETURNED FROM ES QUERY:', len(df))
            assert size == len(df)
            df = df.drop_duplicates(subset='uid').reset_index(drop=True)
            df.to_csv(results_fp, index=False)

    df['keyword_label'] = df['body'].apply(lambda x: label_text_from_dict(document_text=x, label_dict=LABELS_DICT))
    print('TOTAL DATA POINTS FROM CSV: ', len(df))
    # SINCE THERE CAN BE MULTIPLE KEYWORDS IN A DOCUMENT, WE NEED TO DUPLICATE THOSE WITH MULTIPLE LABELS, AND
    # MAKE A NEW DATA FRAME TO REPRESENT ALL KEYWORDS.

    #### MAKE A SECOND DATAFRAME WITH MENTIONS OF MULTIPLE KE SUBJECTS

    mult_df = df.loc[df['keyword_label'].map(len) > 1]
    mult_df.loc[:, 'keyword_label'] = mult_df.loc[:, 'keyword_label'].apply(lambda x: x[1])

    #### RENAME THE RO SUBJECT AS FIRST ENTRY IN DF AND SECOND ENTRY IN MULT_DF
    df.loc[:, 'keyword_label'] = df.loc[:, 'keyword_label'].apply(lambda x: x[0] if len(x) != 0 else None)

    df = pd.DataFrame(pd.concat([df, mult_df]).reset_index(drop=True))

    df['date'] = pd.to_datetime(df['timestamp']).dt.date
    daily_df = df.groupby(['date', 'keyword_label']).uid.count().reset_index().rename(columns={
        'uid': 'count'}).sort_values('date')
    daily_df.to_csv(os.path.join(project_dirs['data'], 'daily_counts.csv'))

    limits_fp = os.path.join(project_dirs['data'], 'limits.json')
    limits_dict = {}
    labels = list(daily_df['keyword_label'].unique())
    if not os.path.exists(limits_fp):
        for lab in labels:
            conf = conf_intervals_from_category(df=daily_df, value=lab, log=False)
            limits_dict[lab] = conf


    print(limits_dict)
    exit()

    # messages_df = df.resample(f'{interval}D', offset='0m').message_id.count().reset_index().rename(columns={'message_id': int_col})


if __name__ == '__main__':
    main()
