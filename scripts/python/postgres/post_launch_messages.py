import os.path

import matplotlib.pyplot as plt
import numpy as np
from scipy import interpolate
from odin.collect.postgres import Db
import pandas as pd
from datetime import timedelta
import odin.utils.projects as proj
import seaborn as sns
import statsmodels.api as sm
from statsmodels.formula.api import ols
import logging
logger = logging.getLogger(__name__)

#### GIVEN A DATE, OR SET OF DATES...
# 1. HOW MANY MESSAGES DID RFJ RECEIVE AFTER THOSE DATES?
# 2. IF AND INCREASE IN MESSAGE TRAFFIC EXISTS, HOW LONG DOES THE INCREASE LAST?


# OBJECTIVE: Assess the tips volume after a campaign launch.
#
# Process:
# Look at the two days following a campaign launch (utilizing post times from the rfj_usa twitter) and aggregate
# the tips volume from postgres. Assess what the normal volume of messages is for 2 days following.
# Note: it may be valuable to breakdown the interval into hours and study what different hourly volumes are. For
# example, 4, 8, 12, etc hour intervals for each campaign and see when the messages start to decrease...assuming
# the volume does in fact increase from the message volume while not running a campaign within 2 days. This will require
# assessing the message volume that is not within two days of a campaign launch (post date) and comparing the two
# samples.

# sample message data within two days of post dates.
# sample message data not within two days of post dates. get the diff between post dates if greater than ~5, then we
# can sample between those two posts as long as the days between that and the next post ar greater than 2 days.

# todo: add histograms and boxplots for each post date
# todo: query all the relevant data stuff a few days after a post...aggregate by day, establish expected message in
#  after a post
# todo: could also try and find the most common day we hit the most messages within ten days following a post

def main():

    ### SCRIPT INPUTS
    proj_dir = os.path.expanduser('~/projects/odin/post_launch_messages')
    sub_dirs = ['plots', 'data']
    proj_dict = proj.setup_project_directory(proj_dir, sub_dirs)
    interval = 5

    int_col = f'day_count'

    posts_fp = '~/data/odin/social_media/hootsuite/twitter_post_performance_2021-08-13_to_2023-02-28_created_on_' \
               '20230327T2015Z_twitter_post_performance.csv'

    ### RFJ POST DATES IN GMT ###
    posts_df = pd.read_csv(os.path.expanduser(posts_fp))

    posts_df = posts_df.loc[posts_df['Twitter Account'] == '@RFJ_USA']
    post_dates = posts_df['Date (GMT)'].tolist()
    post_dates.reverse()

    diffs = pd.Series.round((pd.Series(pd.to_datetime(post_dates)).diff().iloc[1:] / timedelta(days=1)), 0).astype(int)
    idxs = diffs.loc[diffs > interval].index

    ### RFJ NON POST DATES WITH 2 DAYS PRIOR TO POST
    non_post_dates = pd.to_datetime([pd.to_datetime(post_dates[idx]) + timedelta(days=-2) for idx in idxs]).date
    start_datetime = post_dates[0]  # QUERY START TIME
    end_datetime = str(pd.to_datetime(post_dates[-1]) + timedelta(days=interval))  # QUERY ENDTIME
    fp = os.path.join(proj_dict['data'], f'{start_datetime}_{end_datetime}_messages.csv')

    ### GET THE POSTGRES DATA
    df = []
    if not os.path.exists(fp):
        with Db.Create('DEV') as db:
            data = db.get_messages_by_datetime(start_datetime=start_datetime, end_datetime=end_datetime, direction='in')

        df = pd.DataFrame(data)
        df.to_csv(fp, index=False)
    elif os.path.exists(fp):

        df = pd.read_csv(fp)

    df['date'] = pd.to_datetime(df['datetime']).dt.date
    df['datetime'] = pd.to_datetime(df['datetime'])

    ### DEFINE THE POST CAMPAIGN DATA
    data = {}
    df = df.set_index(['datetime'])

    # todo: write helper functions for this in Odin...
    messages_df = df.resample(f'{interval}D', offset='0m').message_id.count().reset_index().rename(columns={'message_id': int_col})
    messages_df['date'] = messages_df['datetime'].dt.date
    messages_df = messages_df.loc[messages_df[int_col] > 0]
    messages_df['log10_count'] = np.log10(messages_df[int_col])

    mask = pd.Series(pd.to_datetime(post_dates).date).unique().tolist()
    post_launch_df = messages_df.loc[messages_df['date'].isin(mask)].reset_index()
    not_post_df = messages_df.loc[messages_df['date'].isin(non_post_dates)].reset_index()

    dfs = {'ALL MESSAGE DATA': messages_df,
           'POST LAUNCH DATA': post_launch_df,
           'NON LAUNCH DATA': not_post_df}
    sizes = [len(dfs[key]) for key in dfs]

    sample = 30
    if min(sizes) < 30:
        sample = min(sizes)
    f, axs = plt.subplots(nrows=len(dfs.keys()), ncols=2, figsize=(10, 10))
    names = list(dfs.keys())

    t_data = []
    for idx in enumerate(axs):
        index = idx[0]

        name = names[index]
        tmp = dfs[name]
        tmp = pd.DataFrame(tmp).sample(n=sample, random_state=1).sort_values(by='date')
        print(f'{name} \n:', tmp)
        x = tmp.date
        y = tmp['log10_count']
        axs[index, 0].set_title(f'log10 time plot: {name} \n mean: {np.mean(y).round(3)}, n: {len(y)}')
        axs[index, 0].scatter(x, y)
        axs[index, 1].set_title(f'log 10 histogram: {name} \n mean: {np.mean(y).round(3)}, n: {len(y)}')
        axs[index, 1].hist(y, ec='w')

        axs[index, 0].set_xticks([min(x), max(x)])
        axs[index, 0].set_xticklabels(labels=[min(x), max(x)], rotation=45, ha='right')
        if not name == 'ALL MESSAGE DATA':
            tmp['type'] = name
            t_data.append(tmp)

    t_df = pd.concat(t_data)[['log10_count', 'type']]
    print(t_df)

    f.suptitle(f'Plots with {interval} Day Counts', size=20)
    plt.tight_layout()
    fp = os.path.join(proj_dict['plots'], f'{interval}_message_plots.png')

    f.savefig(fp)

    f, ax = plt.subplots(figsize=(10, 10))
    ax = sns.boxplot(x='type', y='log10_count', data=t_df, color='#99c2a2')
    f.suptitle(f'Boxplots and ANOVA for {interval} Day Counts')

    model = ols('log10_count ~ C(type)', data=t_df).fit()
    anova_table = sm.stats.anova_lm(model, typ=2)
    rows = []
    for r in range(len(anova_table)):

        # todo: try to round the values and make table cleaner

        row = list(anova_table.iloc[r])
        rows.append(row)

    row_labels = list(anova_table.index)
    col_labels = list(anova_table.columns)
    table = plt.table(cellText=rows,
                      colWidths=[0.2] * 4,
                      rowLabels=row_labels,
                      colLabels=col_labels,
                      loc='top')
    print(anova_table)
    plt.tight_layout()
    fp = os.path.join(proj_dict['plots'], f'{interval}_days_boxplot.png')
    f.savefig(fp)


    # todo: evaluate and delete...
    # exit()
    #
    # axs[0, 0].plot(messages_df.index, messages_df[int_col])
    # axs[0, 1].hist(np.log10(messages_df[int_col]), ec='w', ha='right')
    # # ax.set_xticks(messages_df['datetime'])
    # # ax.set_xticklabels(labels=messages_df['datetime'], rotation=90)
    # # todo: bigger num = smoother...what is good ratio?
    # xnew = np.linspace(start=min(messages_df.index), stop=max(messages_df.index), num=1000)
    # bspline = interpolate.make_interp_spline(messages_df.index, messages_df[int_col])
    # ynew = bspline(xnew)
    # axs[0, 0].plot(xnew, ynew)
    #
    # axs[1, 0].plot(post_launch_df.index, post_launch_df[int_col])
    # axs[1, 1].hist(np.log10(post_launch_df[int_col]), ec='w')
    # axs[2, 0].plot(not_post_df.index, not_post_df[int_col])
    # axs[2, 1].hist(np.log10(not_post_df[int_col]), ec='w')
    # plt.tight_layout()
    # plt.show()
    # exit()
    # messages_df['date'] = messages_df['datetime'].dt.date
    # messages_df = messages_df.loc[messages_df['date'].isin(pd.to_datetime(pd.Series(post_dates)).dt.date)]
    # counts = messages_df[int_col]
    # f, ax = plt.subplots(figsize=(10, 10))
    # ax.hist(counts, ec='w')
    # print(counts)
    # plt.show()
    # exit()
    #
    #
    # for date in enumerate(post_dates):
    #     post_date = pd.to_datetime(date[1]).date()
    #     delta = post_date + timedelta(days=2)
    #     mask = (df['date'] >= post_date) & (df['date'] <= delta)
    #     messages_df = df.loc[mask]
    #     sum_df = pd.DataFrame(messages_df.groupby('date').message_id.count().reset_index().rename(columns={'message_id': 'count'}))
    #     sum_df['log10_count'] = np.log10(sum_df['count'])
    #     if post_date not in data:
    #         if len(sum_df) == interval + 1:
    #             data[post_date] = sum_df
    #
    # # f, axs = plt.subplots(nrows=len(data.keys()), figsize=(10, 10))
    # f, ax = plt.subplots(figsize=(10, 10))
    # for date in data.keys():
    #     messages_df = data[date]
    #     integers = range(11)
    #     ax.plot(integers, messages_df['log10_count'])
    #
    # plt.tight_layout()
    # plt.show()
    # # print(list(data.values()))
    #
    # print(len(data), len(post_dates))




if __name__ == '__main__':
    main()

