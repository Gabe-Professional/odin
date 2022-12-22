import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import re
import os




def get_reward_offer_amount(text):
    # todo: need to filter out phone numbers...


    # todo: would be nice to know if the website address was used
    # if 'http://www.rewardsforjustice.net' in text:
    #     print('http://www.rewardsforjustice.net')
    # print(text)
    text = re.split('https:\/\/.*', str(text))[0]
    text = re.split('http:\/\/.*', str(text))[0]

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


def main():
    ###### SET THE VARIABLES ######
    pd.set_option('display.max_rows', None)
    metric = 'engagements'
    x = 'reward_amount'
    # directory = os.path.join('~', 'output', 'odin', 'twitter_effectiveness')
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
    N = len(df)


    # df = df[df['reward_offer_post?'] == 1]

    df = df[df[metric] > 0]
    n_var = len(df)
    data = {'log_impressions': np.log10(df['impressions']),
            'log_engagements': np.log10(df['engagements']),
            'reward_offer_post?': df['reward_offer_post?'],
            'reward_amount': df['reward_amount']}
    data_df = pd.DataFrame(data)
    tmp = data_df[data_df[x] > 0]
    n_pos_ro = len(tmp)
    ro_amts = tmp[x].unique()
    n_ro_amts = len(ro_amts)

    f, axs = plt.subplots(figsize=(10, 10), nrows=n_ro_amts)

    for tup in enumerate(ro_amts):
        i = tup[0]
        n = len(tmp[tmp[x] == ro_amts[i]])
        axs[i].hist(tmp[tmp[x] == ro_amts[i]][f'log_{metric}'], ec='w')
        axs[i].set_title(f'RO Amount: {ro_amts[i]}, n: {n}')

    plt.tight_layout()
    fp = os.path.join(directory, f'{metric}_{x}_histogram.png')
    f.savefig(fp)

    print(f'Total initial data points: {N} \n'
          f'Total data points {metric} > 0: {n_var} \n'
          f'Unique reward offer amounts: {n_ro_amts} \n'
          f'Data points with RO > 0: {n_pos_ro}')

    # todo: run multiple iterations with different sample sizes

    sample_size = 100
    f, ax = plt.subplots(nrows=2, figsize=(10, 10))
    tmp = data_df[data_df[x] > 0]
    ax[0].hist(tmp[f'log_{metric}'], ec='w')
    n_tmp = len(tmp)
    x_bar = np.mean(tmp[f'log_{metric}']).round(decimals=3)
    v = np.var(tmp[f'log_{metric}']).round(decimals=3)
    ax[0].set_title(f'n > 0: {n_tmp}, mean: {x_bar}, var: {v}')


    tmp = data_df[data_df[x] == 0]
    ax[1].hist(tmp[f'log_{metric}'], ec='w')
    n_tmp = len(tmp)
    x_bar = np.mean(tmp[f'log_{metric}']).round(decimals=3)
    v = np.var(tmp[f'log_{metric}']).round(decimals=3)
    ax[1].set_title(f'n = 0: {n_tmp}, mean: {x_bar}, var: {v}')

    plt.tight_layout()

    f.savefig(os.path.join(directory, '0vsRO_histogram.png'))


if __name__ == '__main__':
    main()
