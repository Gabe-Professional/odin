import gensim.models
import matplotlib.pyplot as plt
import numpy as np
from gensim import corpora, models
from odin.utils.projects import setup_project_directory
import os
import pandas as pd
from odin.collect.postgres import Db
from odin.collect.pulse_api import Api
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, confusion_matrix
from odin.utils.munging import parse_vector_string, preprocess_text, \
    make_topic_str, make_word_freq_df, get_domain_words


def main(args):
    # Setup the project directory
    version = 'v3'
    mod = args.model
    retrain = args.retrain
    subdirs = ['data', 'plots', 'model']
    proj_dir = f'~/projects/odin/spam_messages/{version}/{mod}'
    test_contacts = [792]

    dirs = setup_project_directory(directory=proj_dir, subdirs=subdirs)

    domain_words_fp = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(dirs['data']))), 'words.txt')

    rand_size = 5000
    rand = False
    if args.start and args.end:
        messages_fp = os.path.join(dirs['data'], f'{args.start}_{args.end}_messages.csv')
    else:
        rand = True
        messages_fp = os.path.join(dirs['data'], f'{rand_size}_rand_messages.csv')

    # Some data for text processing
    custom_words = ['hello', 'hi', 'hey', 'al', 'like', 'inform', 'com', 'gmail', 'pdf', 'money', 'want',
                    'page', 'use', 'see', 'one', 'number', 'also', 'icj', 'give', 'org', 'reward', 'digit', 'know',
                    'abroad', 'access', 'account', 'accredit', 'actual', 'ad', 'address', 'affair', 'alert', 'answer', 'appoint', 'area', 'armadillo', 'around', 'ask', 'aspect', 'assist', 'attach', 'attack', 'attent', 'avail', 'away', 'backup', 'base', 'batch', 'best', 'big', 'border', 'born', 'bot', 'boy', 'branch', 'brook', 'brother', 'brutal', 'build', 'call', 'cannot', 'captain', 'case', 'caution', 'certain', 'chat', 'check', 'citizen', 'citizenship', 'civil', 'claim', 'click', 'coast', 'collect', 'colonel', 'color', 'combat', 'come', 'concern', 'confront', 'consist', 'construct', 'consult', 'correspond', 'court', 'cream', 'creat', 'crime', 'cryptograph', 'dam', 'date', 'day', 'death', 'democrat', 'demolish', 'depart', 'develop', 'die', 'dim', 'director', 'discord', 'distrust', 'doctor', 'doe', 'dog', 'doubt', 'earn', 'effect', 'either', 'emir', 'encrypt', 'enough', 'enter', 'erupt', 'even', 'exact', 'expand', 'extremist', 'fact', 'fake', 'far', 'fell', 'fighter', 'fill', 'find', 'fire', 'five', 'flare', 'form', 'free', 'freedom', 'friend', 'gain', 'gave', 'girl', 'given', 'go', 'good', 'gulf', 'guy', 'hack', 'hacker', 'hand', 'help', 'highest', 'hit', 'hold', 'host', 'infect', 'island', 'jabber', 'join', 'jordan', 'key', 'kill', 'kindergarten', 'lane', 'law', 'lawyer', 'leadership', 'legal', 'let', 'level', 'liber', 'lift', 'link', 'liquid', 'list', 'long', 'longer', 'look', 'lotus', 'made', 'manner', 'may', 'meet', 'member', 'met', 'moment', 'move', 'must', 'name', 'neighborhood', 'network', 'night', 'occur', 'offer', 'often', 'opinion', 'option', 'park', 'pass', 'perfect', 'period', 'person', 'pharmacist', 'photo', 'pick', 'plan', 'plea', 'point', 'polo', 'port', 'posit', 'prescript', 'prevent', 'pro', 'progress', 'project', 'proof', 'protect', 'public', 'put', 'quit', 'racism', 'racist', 'rate', 'reach', 'real', 'reckless', 'region', 'regret', 'remain', 'renew', 'republican', 'rest', 'return', 'right', 'robot', 'russia', 'sale', 'sanction', 'sedan', 'seminar', 'send', 'sha', 'side', 'sister', 'site', 'slow', 'sooner', 'sort', 'speak', 'special', 'speech', 'spread', 'still', 'strict', 'strong', 'success', 'suffer', 'sure', 'taken', 'talk', 'target', 'teach', 'tell', 'term', 'terror', 'terrorist', 'therefor', 'think', 'third', 'tire', 'today', 'told', 'tomorrow', 'tool', 'tough', 'track', 'transit', 'travel', 'trump', 'two', 'type', 'understand', 'unit', 'veri', 'via', 'victim', 'video', 'vigil', 'virus', 'visa', 'wealth', 'weapon', 'weekend', 'white', 'write', 'yes', 'yesterday']
    custom_stem = {'syrian': 'syria',
                   'russian': 'russia',
                   'elections': 'election'}
    # List of words to remove messages. These are Non text interactions usually.
    # This removes all PG results that are not text messages...
    messages_to_remove = ['Video', 'Sticker', 'photo', 'voice']
    # Create a regex pattern to match any word from the list
    pattern = '|'.join(rf'\b{word}\b' for word in messages_to_remove)
    domain_words = get_domain_words(domain_words_fp)

    state = 1

    # Get the message data
    if os.path.exists(messages_fp):
        messages_df = pd.read_csv(messages_fp)
        messages_df = messages_df.loc[~messages_df['message'].isna()]
        messages_df = messages_df[~messages_df['message'].str.contains(pattern, case=False, na=False, regex=True)]
    else:
        with Db.Create('DEV') as pg:
            if rand:
                messages_df = pg.get_random_messages_in(size=rand_size)
            else:

                messages_df = pg.get_messages_by_datetime(start_datetime=args.start,
                                                          end_datetime=args.end,
                                                          direction='in')

            messages_df['machine_translation'] = messages_df['machine_translation'].fillna('')
            messages_df['machine_translation'] = messages_df.apply(lambda row:
                                                                   row['message']
                                                                   if len(row['machine_translation']) == 0
                                                                   else row['machine_translation'], axis=1)

            messages_df = messages_df.loc[~messages_df['message'].isna()]
            messages_df = messages_df[~messages_df['message'].str.contains(pattern,
                                                                           case=False,
                                                                           na=False,
                                                                           regex=True)]

            if mod == 'svm':
                if 'labse' not in messages_df.columns:
                    print('GETTING LABSE FOR MESSAGES...')
                    messages_df['labse'] = messages_df['message'].apply(lambda x:
                                                                        Api.Create('DEV').make_request(text=x,
                                                                                                       method='post'))

            messages_df.to_csv(messages_fp, index=False)

    messages_df['threat_words'] = list(map(lambda text:
                                           list(set(word for word in text.split() if word.lower() in domain_words)),
                                           messages_df['machine_translation']))

    # Run train the svm model
    if mod == 'svm':
        messages_df['threat?'] = messages_df['threat_words'].apply(lambda x: 1 if len(x) > 0 else 0)
        messages_df['labse'] = messages_df['labse'].apply(lambda x: parse_vector_string(x, value_type='str'))
        messages_df = messages_df.dropna(subset=['labse'])
        # messages_df = messages_df.loc[messages_df['machine_translation'].isin(test_contacts)]
        messages_df['labse'] = messages_df['labse'].apply(lambda x: x if len(x) > 0 else [0] * 768)
        # Get a sample dataset to label
        train_data, test_data, train_labels, test_labels = train_test_split(
            messages_df['labse'], messages_df['threat?'], test_size=.2, random_state=state)

        train_sum = train_labels.value_counts().reset_index()
        train_sum['prop'] = train_sum['count'] / sum(train_sum['count'])
        train_sum.loc['sum'] = train_sum[['count', 'prop']].sum(axis=0)

        test_sum = test_labels.value_counts().reset_index()
        test_sum['prop'] = test_sum['count'] / sum(test_sum['count'])
        test_sum.loc['sum'] = test_sum[['count', 'prop']].sum(axis=0)
        print('training sample: \n', train_sum.fillna(''))
        print('test sample: \n', test_sum.fillna(''))

        x_train = train_data.to_list()
        x_test = test_data.to_list()

        # todo: replace this with run numbers
        # ml_models = {'SVM': SVC()}
        class_names = messages_df['threat?'].unique().tolist()
        # Run each model classifier
        classifier = SVC()
        classifier.fit(x_train, train_labels)

        # Get predictions on the test data
        predictions = classifier.predict(x_test)

        accuracy = accuracy_score(test_labels, predictions)
        confusion_matrix_str = f"{mod} Confusion Matrix: Accuracy: {accuracy: .2f} \n"
        confusion_matrix_str += "Act/Pred  " + "   ".join([str(c) for c in class_names]) + "\n"
        cfm = confusion_matrix(test_labels, predictions)

        # todo: make a function to produce dynamic confusion matrix.
        for i, row in enumerate(cfm):
            confusion_matrix_str += ' ' * 4 + f"{class_names[i]}     "
            confusion_matrix_str += "  ".join(map(str, row)) + "\n"

        print(f'{mod} Accuracy: {accuracy: .2f}')
        print(f'{confusion_matrix_str}')

    elif mod == 'lda':
        # todo: move the remove custom key stopwords to after stemming...

        # # FILTER FOR PROBABLY ENGLISH AND ARABIC MESSAGES...
        # messages_df = messages_df.loc[messages_df['language'].isin(['ODIN: usa', 'ODIN: arabic'])]
        if ('preprocessed' not in messages_df.columns) or retrain is True:
            messages_df['preprocessed'] = \
                messages_df['machine_translation'].apply(lambda x: preprocess_text(x, domain_words=domain_words,
                                                                                   custom_stem=custom_stem,
                                                                                   custom_stopwords=custom_words,
                                                                                   token=('stem', )))
            messages_df.to_csv(messages_fp, index=False)

        messages_df['preprocessed'] = messages_df['preprocessed'].apply(lambda x:
                                                                        parse_vector_string(x, value_type='str'))
        # messages_df['preprocessed'] = messages_df['preprocessed'].apply(lambda x: ' '.join(x))
        messages_df = messages_df.loc[~messages_df['contact_id'].isin(test_contacts)]
        messages_df = messages_df.sample(n=200, random_state=state)

        lda_train_data, lda_test_data = train_test_split(messages_df['preprocessed'],
                                                         test_size=.2, random_state=1)

        train_lda_text = lda_train_data.to_list()
        test_lda_text = lda_test_data.to_list()

        # USING DIFFERENT METHODS TO FILTER TEXT...
        # train_processed_messages = [message.lower() for message in train_lda_text]
        # test_processed_messages = [message.lower() for message in test_lda_text]

        # train_processed_messages = list(map(lambda text:
        #                                     list(set(word for word in text.split() if word.lower() in domain_words)),
        #                                     train_processed_messages))
        #
        # test_processed_messages = list(map(lambda text:
        #                                    list(set(word for word in text.split() if word.lower() in domain_words)),
        #                                    test_processed_messages))
        # train_processed_messages = [preprocess_text(message, token=('stem',)) for message in train_lda_text]
        # test_processed_messages = [preprocess_text(message, token=('stem',)) for message in test_lda_text]

        train_processed_messages_df = pd.DataFrame({'processed': train_lda_text})
        # train_processed_messages = tmp[tmp['processed'].map(len) > 2]['processed'].to_list()
        test_processed_messages_df = pd.DataFrame({'processed': test_lda_text})
        # test_processed_messages = tmp[tmp['processed'].map(len) > 2]['processed'].to_list()

        pd.set_option('display.max_rows', None)

        # Create a dictionary and corpus for LDA
        dictionary = corpora.Dictionary(train_lda_text)
        test_dictionary = corpora.Dictionary(test_lda_text)
        corpus = [dictionary.doc2bow(text) for text in train_lda_text]
        test_corpus = [test_dictionary.doc2bow(text) for text in test_lda_text]

        train_wrd_frq_df = make_word_freq_df(corpus, dictionary).sort_index(axis=1, ascending=True)
        f, ax = plt.subplots()
        ax.hist(np.log10(train_wrd_frq_df.sum(axis=0)), ec='w')

        # plt.show()
        sum_words = train_wrd_frq_df.sum(axis=0)
        # print(list(sum_words[sum_words < 5].index))

        num_topics = [2]
        for run, nt, in enumerate(num_topics):
            print(f'RUN {run + 1} \n')
            print(f'Number of topics: {nt} \n')
            classifier = gensim.models.LdaModel(corpus, num_topics=nt, id2word=dictionary,
                                                passes=15, random_state=state)

            topics = classifier.print_topics(num_topics=nt)

            lda_str = make_topic_str(lda_topics=topics)

            # test_topic_distributions = [classifier.get_document_topics(doc) for doc in test_corpus]
            test_topic_distributions = []
            count = 0
            for doc in test_corpus:
                try:
                    dist = classifier.get_document_topics(doc)
                    test_topic_distributions.append(dist)
                except:
                    test_topic_distributions.append([(0, 0.5), (0, .5)])

            test_assigned_topics = [max(test_topic_distribution,
                                        key=lambda x: x[1])[0] + 1 for test_topic_distribution in test_topic_distributions]
            train_topic_dists = [classifier.get_document_topics(doc) for doc in corpus]
            train_assigned_topics = [max(train_topic_distribution,
                                         key=lambda x: x[1])[0] + 1 for train_topic_distribution in train_topic_dists]

            train_res = pd.DataFrame({'train_processed': lda_train_data,
                                      'train_topics': train_assigned_topics,
                                      'rank': map(len, lda_train_data)})
            print('Training topics: \n ', train_res)
            train_sum = train_res.groupby('train_topics').train_processed.count()\
                .reset_index().rename(columns={'train_processed': 'count'})

            train_sum['prop'] = train_sum['count'] / sum(train_sum['count'])
            train_sum.loc['SUM'] = train_sum[['count', 'prop']].sum(axis=0)

            test_res = pd.DataFrame({'test_processed': lda_test_data,
                                     'test_topics': test_assigned_topics})
            print('Test Result Topics \n', test_res)

            test_sum = test_res.groupby('test_topics').test_processed.count()\
                .reset_index().rename(columns={'test_processed': 'count'})
            test_sum['prop'] = test_sum['count'] / sum(test_sum['count'])
            test_sum.loc['SUM'] = test_sum[['count', 'prop']].sum(axis=0)

            print('Training topic summary: \n', train_sum)
            print('Test topic summary: \n', test_sum)
            print(lda_str)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--model', choices=['svm', 'lda'])
    parser.add_argument('--start')
    parser.add_argument('--end')
    parser.add_argument('--retrain', action='store_true')

    args = parser.parse_args()
    main(args)
