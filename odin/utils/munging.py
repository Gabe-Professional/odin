import json
import os
import nltk
import numpy as np
import pandas as pd
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import scipy.linalg as la

nltk.download('stopwords')
stpwords = stopwords.words('english')
lemmatizer = WordNetLemmatizer()


# todo: need to move munging stuff to utils directory
def clean_data(data):
    # todo: add argument to import list of desired attributes

    tmp = {'uid': [],
           'timestamp': [],
           'system_timestamp': [],
           'author': [],
           'body': [],
           'body_language': [],
           'domain': [],
           'labse_encoding': [],
           'body_translation': [],
           'follower_count': [],
           'hashtags': []
           }

    for res in data:

        try:
            uid = res['_source']['uid']
        except:
            uid = None
        try:
            auth = res['_source']['norm']['author']
        except:
            auth = None
        try:
            txt = res['_source']['norm']['body']
        except:
            txt = None
        try:
            bl = res['_source']['meta']['body_language'][0]['results'][0]['value']
        except:
            bl = None
        try:
            dom = res['_source']['norm']['domain']
        except:
            dom = None
        try:
            ts = pd.to_datetime(res['_source']['norm']['timestamp'])
        except:
            ts = None
        try:
            sts = pd.to_datetime(res['_source']['system_timestamp'])
        except:
            sts = None
        try:
            en = res['_source']['meta']['ml_labse'][0]['results'][0]['encoding']
        except:
            en = None
        try:
            bt = str(res['_source']['meta']['ml_translate'][0]['results'][0]['text'])
        except:
            bt = None
        try:
            fc = int(res['_source']['meta']['followers_count'][0]['results'][0])
        except:
            fc = None
        try:
            ht = res['_source']['meta']['hashtag'][0]['results']
        except:
            ht = None

        tmp['uid'].append(uid)
        tmp['timestamp'].append(ts)
        tmp['system_timestamp'].append(sts)
        tmp['author'].append(auth)
        tmp['body'].append(txt)
        tmp['body_language'].append(bl)
        tmp['domain'].append(dom)
        tmp['labse_encoding'].append(en)
        tmp['body_translation'].append(bt)
        tmp['follower_count'].append(fc)
        tmp['hashtags'].append(ht)

    pd.set_option('display.max_columns', None)
    df = pd.DataFrame(tmp).drop_duplicates(subset='uid').sort_values(by='system_timestamp')
    return df


# todo: need a function here to input a custom datetime and tz to the .json query
def change_query_datetime(start_time, end_time, query_path):
    with open(query_path) as qp:
        data = json.load(qp)
        data['query']['bool']['filter'][3]['range']['system_timestamp']['gte'] = start_time
        data['query']['bool']['filter'][3]['range']['system_timestamp']['lte'] = end_time
    return data


def parse_vector_string(vector_string):
    try:
        vl = vector_string.replace('[', '').replace(']', '').replace(',', '').split()
        vl = [float(i) for i in vl]
    except:
        vl = None
    return vl


def text_tokenize(string, add_stopwords=list(), min_word_length=3):

    if len(add_stopwords) > 0:
        stpwords.extend(add_stopwords)
    tokens = nltk.word_tokenize(string)
    text_fix = list(filter(lambda token: nltk.tokenize.punkt.PunktToken(token).is_non_punct, tokens))

    text_fix = [word.lower() for word in text_fix]
    text_fix = list(filter(lambda token: token not in stpwords, text_fix))
    text_fix = [word for word in text_fix if len(word) >= min_word_length]
    text_fix = [lemmatizer.lemmatize(word) for word in text_fix]
    text_fix = ' '.join(text_fix)
    return text_fix


def pca(data, nRedDim=0, normalise=1):
    m = np.mean(data, axis=0)
    data -= m
    C = np.cov(np.transpose(data))

    evals, evecs = np.linalg.eig(C)
    indices = np.argsort(evals)
    indices = indices[::-1]
    evecs = evecs[:, indices]
    evals = evals[indices]

    if nRedDim > 0:
        evecs = evecs[:, :nRedDim]
    if normalise:
        for i in range(np.shape(evecs)[1]):
            evecs[:, i] / np.linalg.norm(evecs[:, i]) * np.sqrt(evals[i])
    x = np.dot(np.transpose(evecs), np.transpose(data))
    y = np.transpose(np.dot(evecs, x)) + m
    return x, y, evals, evecs


def lda(targets: np.array, X: np.array):
    X -= X.mean(axis=0)
    n_X = X.shape[0]
    nDim = X.shape[1]
    Sw = np.zeros((nDim, nDim))
    Sb = np.zeros((nDim, nDim))
    C = np.cov(np.transpose(X))
    classes = np.unique(targets)
    for i in range(len(classes)):
        idxs = np.squeeze(np.where(targets == classes[i]))
        d = np.squeeze(X[idxs, :])
        class_cov = np.cov(np.transpose(d))
        Sw += float(np.shape(idxs)[0]) / n_X * class_cov
    Sb = C - Sw
    ev = la.eig(Sw, Sb)
    evals, evecs = ev[0], ev[1]
    idxs = np.argsort(evals)
    idxs = idxs[::-1]
    evecs = evecs[:, idxs]
    evals = evals[idxs]
    w = evecs[:, :]
    X = np.dot(X, w)
    return X, w


def label_document(label_text: str, doc_text: str):
    doc_text = doc_text.lower()
    if label_text in doc_text:
        cls = 1
    else:
        cls = 0
    return cls
