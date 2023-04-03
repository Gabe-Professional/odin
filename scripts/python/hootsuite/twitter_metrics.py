import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import re
import os
import scipy.stats as stats
import statsmodels.api as sm
from statsmodels.formula.api import ols
import seaborn as sns


# todo: need to make text processing utils

def remove_websites(text):
    text = re.split('https:\/\/.*', str(text))[0]
    text = re.split('http:\/\/.*', str(text))[0]
    return text


def get_reward_offer_amount(text):
    # todo: need to filter out phone numbers...


    # todo: would be nice to know if the website address was used
    # if 'http://www.rewardsforjustice.net' in text:
    #     print('http://www.rewardsforjustice.net')
    # print(text)
    # text = re.split('https:\/\/.*', str(text))[0]
    # text = re.split('http:\/\/.*', str(text))[0]
    text = remove_websites(text)

    if '$3' in text:
        return 5
    elif '$5' in text:
        return 5
    elif '$6' in text:
        return 6
    elif '$7' in text:
        return 7
    elif '$10' in text:
        return 10
    elif '$15' in text:
        return 15
    else:
        return 0


def is_reward_offer(text):
    if '$' in text:
        return 1
    else:
        return 0


def has_website(text):
    if 'www.rewardsforjustice.net' in text:
        return 1
    else:
        return 0


def has_string(string: str, body: str):
    if string in body:
        return 1
    else:
        return 0


def get_char_count(text):
    text = remove_websites(text)
    text = text.replace(' ', '')
    l = int(len(text))
    return l


def get_word_count(text: str):
    # todo: remove websites?
    text = remove_websites(text)
    lst = list((filter(('').__ne__, text.split(sep=' '))))

    word_cnt = len(lst)
    return word_cnt


def main():
    ###### SET THE VARIABLES ######
    pd.set_option('display.max_rows', None)
    metric = 'impressions'
    string = '!'
    xs = ['reward_amount', f'has_char']
    variable = xs[1]
    directory = os.path.expanduser('~/output/odin/twitter_effectiveness')
    print(directory)
    filepath = '~/data/odin/social_media/hootsuite/rfj_metrics/all_time/twitter_post_performance_2020-01-01_to_2022-12-19_created_on_20221219T2006Z_twitter_post_performance.csv'
    df = pd.read_csv(filepath)
    df.columns = ['post_time', 'account_name', 'post_id', 'post_link',
                  'post_type', 'post_message', 'post_tag', 'campaign',
                  'author', 'engagement_rate', 'engagements', 'impressions',
                  'likes', 'quote_tweets', 'replies', 'retweets', 'followers_added']

    ###### MAKE SOME ATTRIBUTES ######
    df['reward_amount'] = df['post_message'].apply(lambda x: get_reward_offer_amount(x))
    df['reward_offer_post?'] = df['post_message'].apply(lambda x: is_reward_offer(x))
    df['has_website?'] = df['post_message'].apply(lambda x: has_website(x))
    df[variable] = df['post_message'].apply(lambda x: has_string(string=string, body=x))
    # df['message_length'] = df['post_message'].apply(lambda x: int(len(x)))
    df['message_length'] = df['post_message'].apply(lambda x: get_char_count(x))
    df['word_count'] = df['post_message'].apply(lambda x: get_word_count(x))

    # print(sorted(df['word_count']))
    print(df[['post_message', 'word_count']].sort_values(by='word_count'))

    plt.hist(np.log10(df[df['word_count'] > 20]['word_count']), ec='w')


    N = len(df)

    df = df[df[metric] > 0]
    n_metric = len(df)
    data = {'log_impressions': np.log10(df['impressions']),
            'log_engagements': np.log10(df['engagements']),
            'reward_offer_post?': df['reward_offer_post?'],
            'reward_amount': df['reward_amount'],
            variable: df[variable]}
    data_df = pd.DataFrame(data)
    # tmp = data_df[data_df[xs] > 0]
    n_pos_ro = len(data_df)
    variable_values = data_df[variable].unique()
    n_categories = len(variable_values)

    f, axs = plt.subplots(figsize=(10, 10), nrows=n_categories)

    for tup in enumerate(variable_values):
        i = tup[0]
        n = len(data_df[data_df[variable] == variable_values[i]])
        axs[i].hist(data_df[data_df[variable] == variable_values[i]][f'log_{metric}'], ec='w')
        axs[i].set_title(f'{variable}: {variable_values[i]}, n: {n}')

    plt.tight_layout()
    fp = os.path.join(directory, f'{metric}_{variable}_histogram.png')
    f.savefig(fp)

    print(f'Total initial data points: {N} \n'
          f'Total data points {metric} > 0: {n_metric} \n'
          f'Unique {variable} : {string}: {n_categories} \n'
          f'Data points with valid {variable}: {n_pos_ro}')
    # todo: run multiple iterations with different sample sizes

    sample_size = 100
    state = 1
    # data_df['ro_over_0'] = data_df[xs].apply(lambda a: 1 if a > 0 else 0)
    test_samples = []
    f, ax = plt.subplots(nrows=2, figsize=(10, 10))
    for i in enumerate(variable_values):
        tmp = data_df[data_df[variable] == i[0]].sample(n=sample_size, random_state=state)
        assert len(tmp) == sample_size

        test_samples.append(tmp)
        ax[i[0]].hist(tmp[f'log_{metric}'], ec='w')
        n_tmp = len(tmp)
        x_bar = np.mean(tmp[f'log_{metric}']).round(decimals=3)
        v = np.var(tmp[f'log_{metric}']).round(decimals=3)
        ax[i[0]].set_title(f'variable: {i[0]}, n: {n_tmp}, mean: {x_bar}, variance: {v}')
        ax[i[0]].set_ylabel(metric)
    plt.tight_layout()
    f.savefig(os.path.join(directory, f'{metric}_0vsRO_histogram.png'))
    test_sample_df = pd.concat(test_samples)
    assert len(test_sample_df) == n_categories * sample_size



    #todo: here

    f, ax = plt.subplots(figsize=(10, 10))
    ax = sns.boxplot(x=f'{variable}', y=f'log_{metric}', data=test_sample_df[[f'{variable}', f'log_{metric}']], color='#99c2a2')
    # ax = sns.swarmplot(x=f'ro_over_0', y=f'log_{metric}', data=data_df[['ro_over_0', f'log_{metric}']], color='#7d0013')
    model = ols(f'log_{metric} ~ C(has_char)', data=test_sample_df[[f'{variable}', f'log_{metric}']]).fit()
    anova_table = sm.stats.anova_lm(model, typ=2)

    rows = []
    for r in range(len(anova_table)):
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
    print(type(anova_table))
    plt.tight_layout()
    f.savefig(os.path.join(directory, f'{metric}_{variable}_boxplot.png'))





if __name__ == '__main__':
    main()
