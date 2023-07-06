import os

import matplotlib.pyplot as plt
import numpy as np

from odin.collect.postgres import Db
import pandas as pd
import datetime as DT
import dateparser
from odin.utils.projects import setup_project_directory


# todo: could add this to postgres helper if needed...these are the contacts tables...do the same with messages.
directory = '~/projects/odin/report_dissemination'
proj_dirs = setup_project_directory(directory=directory, subdirs=['data', 'plots'])


prefix_dict = {
    'en': 'tblc88A79sJPpnSyW',
    'tg': 'tbltH5tIPZ2rAChTt',
    'ar': 'tblCiQAYRoeqD1R87',
    'nk': 'tblCfggb54KtFhpX3',
    'ea': 'tblbKOYC1oX8FR0AC',
    'es': 'tblgpxXjGIH8DP1FT',
    'so': 'tblhmrDO1XxCToW6n',
    'fa': 'tbliN8EmoExmpcWyf',
    'sw': 'tblUQWCkqINPc3x3X',
    'fr': 'tblVIRTaS2GjuTxEI',
    'pt': 'tblnLPJ8lBKgihAWH',
    'ru': 'tblZ3QJF3XMXv1xbG'
}

### GET THE REPORT DATA
fp = os.path.join(proj_dirs['data'], 'passed_off_contacts.csv')

df = pd.read_csv(fp)
df['First Pass Off Timestamp'] = \
    df['First Pass Off Timestamp'].apply(lambda x: dateparser.parse(str(x)).astimezone(DT.timezone.utc))

contacts = df['Name'].apply(lambda x: ''.join([i for i in x if not i.isdigit()]))
dates = pd.to_datetime(df['First Pass Off Timestamp']).dt.date
df['prefix'] = contacts
df['date'] = dates
date_max = pd.to_datetime('2023-03-01')

lst = [key.upper() for key in prefix_dict.keys()]
mask = ((df['prefix'].isin(lst)) & (df['date'] < date_max))

### SELECT THE RELEVANT DATA...DATA WITH AN APPROPRIATE CONTACT MAPPING TO A DATABASE...
df = df.loc[mask].reset_index(drop=True)

### GET THE DATA FROM POSTGRES

data = {'id': [],
        'pass_time': [],
        'latest_in_time': [],
        'diff': []}

fp = os.path.join(proj_dirs['data'], 'report_times.csv')

if not os.path.exists(fp):

    for idx, row in pd.DataFrame(df).iterrows():
        name, table, pass_time = row['Name'], prefix_dict[row['prefix'].lower()], row['First Pass Off Timestamp']

        with Db.Create('DEV') as db:
            tmp = db.get_messages_from_contact_id(contact_id=name)
            # print(tmp)

            if len(tmp) > 0:
                if type(tmp[0][1]) is str:
                    latest_in = dateparser.parse(tmp[0][1]).astimezone(DT.timezone.utc)
                    diff = pass_time - latest_in
                    data['id'].append(name)
                    data['pass_time'].append(pass_time)
                    data['latest_in_time'].append(latest_in)
                    data['diff'].append(diff)

    time_df = pd.DataFrame(data)
    time_df.to_csv(fp)
else:
    time_df = pd.read_csv(fp, index_col=0)


time_df['diff'] = pd.to_datetime(time_df['pass_time']) - pd.to_datetime(time_df['latest_in_time'])
pos_df = time_df.loc[time_df['diff'] > DT.timedelta(days=0)]
year = pd.to_datetime(time_df['pass_time']).dt.year
pos_df['year'] = year
dec_days = pos_df['diff'] / DT.timedelta(days=1)
pos_df['decimal_days'] = dec_days
years = pos_df['year'].unique()


f, axs = plt.subplots(nrows=len(years), figsize=(10, 10))
binwidth = 8
mn = min(pos_df['decimal_days'])
# mx = max(pos_df['decimal_days'])
mx = 300
bins = range(int(round(min(dec_days), 0)), int(round(max(dec_days), 0)) + binwidth, binwidth)


for idx, y in enumerate(years):
    binwidth = 10
    tmp = pos_df.loc[pos_df['year'] == y]
    days = tmp['decimal_days']
    n, b, patches = axs[idx].hist(days, ec='w', bins=bins)
    axs[idx].set_xticks(b)
    axs[idx].set_xticklabels(labels=b, rotation=45)
    axs[idx].set_xlim(left=mn, right=mx)
    title = f'Days between last message from contact and report passoff time, \n' \
            f'Year: {y}, n: {len(tmp)}, mean: {np.mean(days).round(3)} days'
    axs[idx].set_title(title)

plt.tight_layout()
fp = os.path.join(proj_dirs['plots'], 'report_times_by_year.png')
f.savefig(fp)



