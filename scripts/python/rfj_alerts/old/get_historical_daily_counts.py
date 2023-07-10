import glob
import json
import os
import matplotlib.pyplot as plt
import pandas as pd
import scipy.stats as stats
import numpy as np
import re
import odin.utils.munging as oum


# todo: get rid of saving all data to a file...

##### FILE PATH VARIABLES #####
LABEL_DIR = 'reward_offer_names'
MAIN_DIR = os.path.expanduser('~/data/odin')
DATA_DIR = os.path.join(MAIN_DIR, f'rfj_alerting/{LABEL_DIR}/data')
DAILY_COUNTS_FP = os.path.join(DATA_DIR, 'daily_counts.csv')
ALL_DOCS_FP = os.path.join(DATA_DIR, 'all_documents.csv')
PLOTS_DIR = os.path.join(MAIN_DIR, f'rfj_alerting/{LABEL_DIR}/plots')
LIMITS_JSON = os.path.join(DATA_DIR, 'labels', 'limits.json')


##### DATA VARIABLES #####
LABELS_DICT = {}
COLUMN_TITLE = 'name_label'
MIN_OBS = 0
MIN_DAILY_DOCS = 0

##### DISPLAY VARIABLES #####
pd.set_option('display.max_rows', None)


def run():
    tmp = pd.read_csv(os.path.join(DATA_DIR, 'labels', 'name_labels.csv'))

    for idx in range(len(tmp)):
        key, label = tmp.iloc[idx, :]['name'], tmp.iloc[idx, :]['label']
        LABELS_DICT[key] = label

    if not os.path.exists(DAILY_COUNTS_FP):
        print('Daily count data file not created. Combining data and saving as daily counts...')
        files = glob.glob(os.path.join(DATA_DIR, '*.csv'))
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

        #### GET THE COUNTS OF EACH RO SUBJECTS MENTIONED EACH DAY
        df = df.loc[df[f'{COLUMN_TITLE}'].map(len) > 0]
        print('TOTAL DOCUMENTS IN DATASET...', len(df))

        df = df.groupby(by=['date', f'{COLUMN_TITLE}'])['uid'].count().reset_index().rename(columns={'uid': 'count'}).sort_values('date')
        df.to_csv(DAILY_COUNTS_FP, index=False)

    else:
        print('Getting daily count data file....{}'.format(DAILY_COUNTS_FP))
        df = pd.read_csv(DAILY_COUNTS_FP)
    print('Total Documents in data: ', sum(df['count']))

    ##### REMOVE DAYS WHERE THE LABEL'S DOCUMENT COUNT IS LESS THAN THE MIN_DAILY DOCS
    df = df.loc[df['count'] >= MIN_DAILY_DOCS]

    if not os.path.exists(LIMITS_JSON):
        df['LN_count'] = np.log(df['count'])

        # df = df.loc[df['count'] > 1]
        cats = list(df.loc[:, f'{COLUMN_TITLE}'].unique())
        limit_dict = {}
        for c in cats:

            tmp = df.loc[df[f'{COLUMN_TITLE}'] == c]
            mu_count = tmp['LN_count'].mean()
            std_count = tmp['LN_count'].std()
            tmp.loc[:, 'norm_count'] = tmp.loc[:, ['LN_count']].apply(lambda x: (x - mu_count) / std_count)
            n = len(tmp)

            # todo: need to check the limits here...add scale to stats intervals
            if n >= MIN_OBS:
                conf = stats.t.interval(alpha=.95, df=len(tmp['LN_count']) - 1, loc=mu_count)
                low = round(conf[0], 4)
                high = round(conf[1], 4)
                n_filt = len(tmp.loc[(tmp.loc[:, 'LN_count'] >= low) & (tmp.loc[:, 'LN_count'] <= high)])
                print(c, conf, round(n_filt / n, 4))
                limit_dict[c] = high

                mu_round = round(mu_count, 4)

                f, ax = plt.subplots(nrows=3, figsize=(10, 10))

                h = ax[0].hist(tmp['LN_count'], ec='w')
                y_lim = h[0].max()

                ax[0].axvline(x=low, color='black')
                ax[0].axvline(x=high, color='black')
                ax[0].axvline(x=mu_round, color='black')

                ax[0].annotate(text=mu_round, xy=(mu_count, y_lim - 1))
                ax[0].annotate(text=low, xy=(conf[0], y_lim - 1))
                ax[0].annotate(text=high, xy=(conf[1], y_lim - 1))

                ax[0].set_title(f'\n n: {len(tmp)}, {COLUMN_TITLE}: {c}')
                ax[0].set_xlabel('LN daily count')

                p = stats.probplot(x=tmp['LN_count'], dist='norm', plot=ax[1])
                rsq = round(p[1][2], 4)
                ax[1].set_title('R^2: {}'.format(rsq))
                ax[2].scatter(x=pd.to_datetime(tmp['date']).dt.date, y=tmp['LN_count'])
                ax[2].axhline(y=low, color='black', ls='dashed')
                ax[2].axhline(y=high, color='black', ls='dashed')
                ax[2].axhline(y=mu_round, color='black', ls='dashed')
                ax[2].set_ylabel('LN Daily Count')
                ax[2].grid()
                plt.xticks(rotation=45, ha='right')

                print(f'Plotting {c}....')
                print('probability plot R squared: ', rsq)
                plt.tight_layout()

                f.savefig(os.path.join(PLOTS_DIR, 'threshold_results', f'{re.sub(pattern="[^A-Za-z0-9 ]+", repl="", string=c)}_plots.png'))
        print('TOTAL LABELS WITH DATA:', len(limit_dict.keys()), limit_dict)
        with open(LIMITS_JSON, 'w') as lj:
            json.dump(limit_dict, lj)

    else:
        with open(LIMITS_JSON, 'r') as lj:
            limit_dict = json.load(lj)
            print('TOTAL LABELS WITH DATA:', len(limit_dict.keys()), limit_dict)


if __name__ == '__main__':
    run()
