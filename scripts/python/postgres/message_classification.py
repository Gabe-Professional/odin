import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import requests
from odin.collect.pulse_api import Api
from odin.collect.postgres import Db
from odin.utils.projects import setup_project_directory
from odin.utils.munging import parse_vector_string, is_useful, preprocess_text
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import os
import random
from gensim import corpora, models
from gensim.models import CoherenceModel
import pyLDAvis
import pyLDAvis.gensim_models
import gensim
import re


def main():

    # Setup the project directory
    dirs = setup_project_directory(directory='~/projects/odin/spam_messages', subdirs=['data', 'plots', 'model'])
    messages_fp = os.path.join(dirs['data'], f'messages_rated.csv')

    # Get the message data
    if os.path.exists(messages_fp):
        messages_df = pd.read_csv(messages_fp)

    else:

        # Get the data from contacts that have a rating
        ratings = ['A', 'B', 'C', 'D', 'E', 'F', 'G']
        query = f'select contact_id, annotation_value from public.annotations ' \
                f'where annotation_value in %s'

        with Db.Create('DEV') as pg:
            rating_dict = dict(pg.query(query_statement=query, query_parameters=ratings))
            random.seed(1)
            contacts = random.sample(list(rating_dict.keys()), k=40)

            # Assign the contact rating to the messages
            messages_df = pg.get_messages_from_contact_id(*contacts)
            messages_df['rating'] = messages_df['contact_id'].apply(lambda x: rating_dict[x])

            print('Running LaBSE vector...')
            # Get the LaBSE vector for the messages for running the supervised models...
            messages_df['labse_vector'] = messages_df['message'].apply(lambda x:
                                                                       Api.Create('DEV').make_request(text=x, method='post'))

            # messages_df['labse_vector'] = messages_df['message'].apply(lambda x:
            #                                                            requests.post("http://localhost:8888",
            #                                                                          json={'text': x})).json()['data']['encoding']
            # res = requests.post("http://localhost:8888", json={'text': messages_df['message'][0]})
            # print(res.json()['data']['encoding'])
            messages_df.to_csv(messages_fp, index=False)

    # messages_df['machine_translation'] = messages_df['machine_translation'].astype(str)
    pd.set_option('display.max_columns', None)
    print('Total messages: ', len(messages_df))
    print(len(messages_df['message_id'].unique()))

    # Do some data manipulation
    messages_df['labse_vector'] = messages_df['labse_vector'].apply(lambda x: parse_vector_string(x))
    messages_df['message_length'] = messages_df['message'].apply(lambda x: len(x))
    messages_df['useful?'] = messages_df['rating'].apply(lambda x: is_useful(x))
    messages_df['contact_id'] = messages_df['contact_id'].astype(int)
    messages_df['message_id'] = messages_df['message_id'].astype(int)

    # Clean some data
    messages_df = messages_df[messages_df['labse_vector'].map(len) > 0]

    ratings_summary = messages_df.groupby('rating').message.count().reset_index().rename(columns={'message': 'count'})
    ratings_summary['proportion'] = ratings_summary['count'] / sum(ratings_summary['count'])

    ratings_summary.loc['Sum'] = ratings_summary[['count', 'proportion']].sum(axis=0)
    contact_ratings_df = messages_df.groupby('rating').contact_id.nunique().reset_index().rename(columns={'contact_id': 'count'})
    contact_ratings_df['proportion'] = contact_ratings_df['count'] / sum(contact_ratings_df['count'])
    contact_ratings_df.loc['Sum'] = contact_ratings_df[['count', 'proportion']].sum(axis=0)
    print('Sample rating breakdown: \n', ratings_summary.fillna(''))
    print('Contact rating breakdown: \n', contact_ratings_df.fillna(''))

    # Inspect some LaBSE features for normalcy
    f, axs = plt.subplots(nrows=2, ncols=2)
    random.seed(1)
    positions = [random.randint(0, 767) for _ in range(4)]

    for idx, pos in enumerate(positions):
        row, col = divmod(idx, 2)
        ax = axs[row, col]
        norm = messages_df['labse_vector'].apply(lambda x: x[pos])
        ax.hist(norm, ec='w')
        ax.set_title(f'LaBSE index: {pos}')
    plt.tight_layout()
    f.savefig(os.path.join(dirs['plots'], 'histograms.png'))

    # Summarize some data
    rating_df = messages_df.groupby('useful?').message.count().reset_index().rename(columns={'message': 'count'})
    rating_df['proportion'] = rating_df['count'] / sum(rating_df['count'])
    rating_df.loc['Sum'] = rating_df[['count', 'proportion']].sum(axis=0)
    print('Sample data rating breakdown: \n', rating_df.fillna(''))
    contact_ratings_df = messages_df.groupby('useful?').contact_id.nunique().reset_index().rename(columns={'contact_id': 'count'})
    contact_ratings_df['proportion'] = contact_ratings_df['count'] / sum(contact_ratings_df['count'])
    contact_ratings_df.loc['Sum'] = contact_ratings_df[['count', 'proportion']].sum(axis=0)

    print('Contact rating breakdown: \n', contact_ratings_df.fillna(''))
    # Split the data sets and do some other data things...
    train_data, test_data, train_labels, test_labels = train_test_split(
        messages_df['labse_vector'], messages_df['useful?'], test_size=.2, random_state=1)

    # Split the data for the lda model
    lda_train_data, lda_test_data, lda_train_labels, lda_test_labels = train_test_split(
        messages_df['machine_translation'], messages_df['useful?'], test_size=.2, random_state=1)

    train_ratings_df = train_labels.groupby(train_labels).count().reset_index(allow_duplicates=True)
    train_ratings_df.columns = ['useful?', 'count']
    train_ratings_df['proportion'] = train_ratings_df['count'] / sum(train_ratings_df['count'])

    test_ratings_df = test_labels.groupby(test_labels).count().reset_index(allow_duplicates=True)
    test_ratings_df.columns = ['useful?', 'count']
    test_ratings_df['proportion'] = test_ratings_df['count'] / sum(test_ratings_df['count'])
    print('Training data rating breakdown: \n', train_ratings_df)
    print('Test data rating breakdown: \n', test_ratings_df)

    x_train = train_data.to_list()
    x_test = test_data.to_list()
    train_lda_text = lda_train_data.to_list()
    test_lda_text = lda_test_data.to_list()
    train_processed_messages = [preprocess_text(message) for message in train_lda_text]
    test_processed_messages = [preprocess_text(message) for message in test_lda_text]
    # Create a dictionary and corpus for LDA
    dictionary = corpora.Dictionary(train_processed_messages)
    test_dictionary = corpora.Dictionary(test_processed_messages)
    corpus = [dictionary.doc2bow(text) for text in train_processed_messages]
    test_corpus = [test_dictionary.doc2bow(text) for text in test_processed_messages]

    class_names = [0, 1]
    reports = {}

    # Train the ml_models and store in a dictionary to call later on...
    ml_models = {'GNB': GaussianNB(),
                 'SVM': SVC(),
                 'LDA': [gensim.models.LdaModel(corpus, num_topics=num_topics,
                                                id2word=dictionary, passes=15,
                                                random_state=1) for num_topics in range(3, 7)]}

    # Output the topics of the LDA models
    # todo: could probably handle this better...
    topics = [ml_models['LDA'][m].print_topics(
        num_topics=ml_models['LDA'][m].num_topics) for m in range(len(ml_models['LDA']))]

    # Test the ml_models and produce some results in a text file.
    with open(os.path.join(dirs['data'], 'results.txt'), 'w') as f:
        for mod in ml_models:

            # Get the supervised model results (GNB, SVM)
            if mod != 'LDA':

                classifier = ml_models[mod]
                classifier.fit(x_train, train_labels)

                # Get predictions on the test data
                predictions = classifier.predict(x_test)
                accuracy = accuracy_score(test_labels, predictions)
                confusion_matrix_str = f"{mod} Confusion Matrix: Accuracy: {accuracy: .2f} \n"
                confusion_matrix_str += "Actual/Predicted  " + "   ".join([str(c) for c in class_names]) + "\n"
                cfm = confusion_matrix(test_labels, predictions)

                for i, row in enumerate(cfm):
                    confusion_matrix_str += ' ' * 12 + f"{class_names[i]}     "
                    confusion_matrix_str += "  ".join(map(str, row)) + "\n"

                print(f'{mod} Accuracy: {accuracy: .2f}')
                print(f'{confusion_matrix_str}')

                # Add the classification report text to the reports dictionary for later
                reports[mod] = classification_report(test_labels, predictions)
                print(f'{mod} Classification Report: \n', reports[mod])

            elif mod == 'LDA':

                lda_str = 'LDA Model Results: \n\n'
                for run, topic in enumerate(topics):
                    lda_str += f'Run {run + 1}: \n'
                    perp = ml_models[mod][run].log_perplexity(test_corpus)
                    co_mod_lda = CoherenceModel(model=ml_models[mod][run],
                                                texts=train_processed_messages, dictionary=dictionary, coherence='c_v')

                    co_score = co_mod_lda.get_coherence()

                    lda_str += f'Perplexity: {perp: .2f} \n'
                    lda_str += f'Coherence Score: {co_score: .2f} \n'
                    for item in topic:
                        top = item[0] + 1
                        features = item[1]

                        feature_words = re.findall(r'"(.*?)"', str(features))
                        lda_str += f'Topic {top} : {", ".join(feature_words)} \n'

                    topic_distributions = [ml_models[mod][run].get_document_topics(doc) for doc in test_corpus]
                    assigned_topics = [max(topic_distribution, key=lambda x: x[1])[0] for topic_distribution in
                                       topic_distributions]

                # Add the LDA results string to the reports dictionary
                confusion_matrix_str = ''
                reports[mod] = lda_str

            # Write the results to the results.txt file for each model...
            f.write(f'{mod} Classification Report:\n{reports[mod]}\n')
            f.write(f'{confusion_matrix_str} \n\n')

        # Combine the results with the overview...doing this manually is best for now...
    print('DONE')


if __name__ == '__main__':
    main()