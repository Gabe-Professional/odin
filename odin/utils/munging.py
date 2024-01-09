import collections
import json
import logging
import os
import nltk
import numpy as np
import pandas as pd
from nltk.stem import WordNetLemmatizer
from nltk.stem import SnowballStemmer
from multiprocessing import Pool
from functools import partial
import scipy.linalg as la
import re
from nltk.corpus import stopwords, words
nltk.download("words", quiet=True)
nltk.download("stopwords", quiet=True)

logger = logging.getLogger(__name__)


REWARD_OFFER_NAMES = ["william higgins", "abd al-rahman al-maghrebi",
                      "abdelbasit alhaj alhassan haj hamad", "abdelkarim hussein mohamed al-nasser",
                      "abdelrahman abbas rahama", "abdelraouf abu zaid mohamed hamza", "abderraouf ben habib jdey",
                      "abdikadir mohamed abdikadir", "abdikadir mumin", "abdiqadir mu’min", "abdolreza rahmani fazli",
                      "abdul rahman yasin", "abdul reza shahla'i", "abdul saboor", "abdul wali", "abdul zakir",
                      "abdulbari al-kotf", "abdullah ahmed abdullah", "abdullah nowbahar", "abdullahi osman mohamed",
                      "abdullahi yare", "abu ‘abd al-karim al-masri", "abu huzeifa", "abu mus’ab al-barnawi",
                      "abu oubeïda youssouf al annabi", "abu ubaidah (direye)", "abu ubaydah yusuf al-anabi",
                      "abu-muhammad al-shimali", "abu-yusuf al-muhajir", "abubakar shekau", "abukar ali adan",
                      "adham husayn tabaja", "adnan abu walid al-sahrawi", "adnan hussein kawtharani", "ahadon adak",
                      "ahlam ahmad al-tamimi", "ahmad ibrahim al-mughassil", "ahmed iman ali", "al mahmoud ag baye", "al-shabaab", "al-shabaab's financial mechanisms", "ali al-sha'ir", "ali atwa", "ali gholam shakuri",
                      "ali mohamud rage", "ali qasir", "ali saade", "ali saed bin ali el-hoorie",
                      "ali sayyid muhamed mustafa al-bakri", "ali youssef charara", "amadou koufa", "amir dianat",
                      "amir muhammad sa’id abdal-rahman al-mawla", "anatoliy sergeyevich kovalev",
                      "artem valeryevich ochichenko", "ayman al-zawahiri", "aziz haqqani", "bashir mohamed mahamoud",
                      "carlos alberto garcia camargo", "cemil bayik", "cholo abdi abdullah", "clíver alcalá cordones",
                      "daniel pearl", "dave mankins", "diosdado cabello rondón", "duran kalkan", "earl goen",
                      "evgeny viktorovich gladkikh", "faker ben abdelaziz boussora", "faruq al-suri",
                      "fuad mohamed khalaf", "fuad shukr", "general muhammad hussein-zada hejazi", "gulmurod khalimov",
                      "hafiz abdul rahman makki", "hafiz saeed", "hamad el khairy", "hamed abdollahi",
                      "hamid al-jaziri", "hasan izz-al-din", "hasan nasrallah", "hasib muhammad hadwan",
                      "hassan afgooye", "hassan yaqub ali", "haytham ‘ali tabataba’i", "hebrew university bombing",
                      "henry castellanos garzón", "hernan dario velasquez saldarriaga", "hugo carvajal barrios",
                      "husayn muhammed al-umari", "hussein ali fidow", "ibrahim ahmed mahmoud al-qosi",
                      "ibrahim al-banna", "ibrahim haji jama", "ibrahim ousmane", "ibrahim salih mohammed al-yacoub",
                      "ibrahim taher", "ihsan ashour", "ismail haniyeh", "issa barrey", "issa jimaraou", "iyad ag ghali",
                      "jaber a. elbaneh", "jafar", "jamal saeed abdul rahim", "jehad serwan mostafa",
                      "jerel duane shaffer", "joel wesley shrum", "john granville", "junzō okudaira",
                      "kevin scott sutay", "khalid saeed al-batarfi", "khalil al-rahman haqqani", "khalil yusif harb",
                      "ma’alim daud", "maalim ayman", "maalim salman", "mahad karate", "malik abou abdelkarim",
                      "mangal bagh", "manssor arbabsiar", "marat valeryevich tyukov", "mark randall frerichs",
                      "mark rich", "mikhail mikhailovich gavrilov", "mohamed makawi ibrahim mohamed", "mohamed rage",
                      "mohammad ibrahim bazzi", "mohammed ali hamadei", "mohanad osman yousif mohamed",
                      "mu‘taz numan ‘abd nayif najm al-jaburi", "mufti noor wali mehsud",
                      "muhammad abdullah khalil hussain ar-rahayyal", "muhammad ahmed al-munawar",
                      "muhammad al-jawlani", "muhammad ja'far qasir", "muhammad kawtharani",
                      "muhammad khadir musa ramadan (abu bakr al-gharib)", "muhammad qasim al-bazzal",
                      "murat karayilan", "musa asoglu", "noé suárez rojas", "ousmane illiassou djibo",
                      "pavel aleksandrovich akulov", "pavel valeryevich frolov", "peter kilburn",
                      "petr nikolayevich pliskin", "poula n’gordie", "radullan sahiron",
                      "ramadan abdullah mohammad shallah", "rick tenenoff", "robert a. levinson",
                      "sa’ad bin atef al-awlaki", "sajid mir", "sajjad kashian", "salih al-aruri",
                      "salim jamil ayyash", "salman raouf salman", "sami al-uraydi", "sami jasim muhammad al-jaburi",
                      "sanaullah ghafari", "sayf al-adl", "seher demir sen", "seka musa baluku",
                      "sergey vladimirovich detistov", "seyyed mohammad hosein musa kazemi", "sirajuddin haqqani",
                      "steve welsh", "tahil sali", "talal hamiyah", "tareck zaidan el aissami maddah", "thomas hargrove", "timothy van dyke", "wadoud muhammad hafiz al-turki", "william buckley", "yahya haqqani",
                      "yasin al-suri", "yasin kilwe", "yusef ali miraj", "zerrin sari", "ziyad al-nakhalah",
                      "zulkarnaen", "suellen tennyson"]

# todo: probably should converge like organizations...i.e. hizballah and saudi hizballah...
ORGANIZATION_NAMES = ["15 may organization", "abu nidal organization", "abu sayyaf group", "al-mourabitoun",
                      "al-nusrah front", "al-qa'ida", "al-qa'ida in iraq", "al-qa'ida in the arabian peninsula",
                      "al-qa'ida in the islamic maghreb", "al-qa'ida in the lands of the two niles", "al-shabaab",
                      "ansar al-dine", "ansar al-tawhid", "egyptian islamic jihad", "haqqani network",
                      "harakat al-muqawama al-islamiya", "hayat tahrir al-sham", "hizballah", "hurras al-din",
                      "isis in the greater sahara", "islamic revolutionary guard corps",
                      "islamic revolutionary guard corps-qods force", "islamic state in iraq and syria",
                      "islamic state west africa province", "islamic state's khorasan province",
                      "jama’at nusrat al-islam wal-muslimin", "jamaat-ul-ahrar", "japanese red army",
                      "jemaah islamiya", "kurdistan workers party", "lashkar-e tayyiba",
                      "moro national liberation front", "movement for unity and jihad in west africa",
                      "revolutionary organization 17 november", "revolutionary people’s liberation party/front",
                      "revolutionary struggle", "saudi hizballah", "tehrik-e taliban pakistan"]


REWARD_OFFER_NAMES_DICT = {name: name for name in REWARD_OFFER_NAMES}
ORGANIZATION_NAMES_DICT = {re.sub(pattern="[^A-Za-z0-9 ]+", repl='', string=org): org for org in ORGANIZATION_NAMES}


def parse_vector_string(vector_string, value_type: str):
    if not value_type:
        raise ValueError('Please provide a value type for the elements in your string')

    else:
        if type(vector_string) == str:
            try:
                vl = vector_string.replace('[', '').replace(']', '').replace(',', '').split()
                if value_type == 'float':
                    vl = list(float(i) for i in vl)
                elif value_type == 'str':
                    vl = list(str(i).replace("'", '') for i in vl)
                else:
                    raise ValueError('float and str are the only supported value types at this time')
            except:
                vl = None
        elif type(vector_string) == list:
            vl = vector_string
        else:
            vl = None
    return vl


def text_tokenize(string, add_stopwords=list(), min_word_length=3):
    nltk.download('stopwords', quiet=True)
    stpwords = stopwords.words('english')
    lemmatizer = WordNetLemmatizer()

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


def label_text_from_dict(document_text: str, label_dict=None):
    doc_text = re.sub(r'http\S+', '', str(document_text).lower())
    # doc_text = re.sub(pattern="[^A-Za-z0-9 ]+", repl="", string=doc_text)
    doc_text = re.sub(pattern="[@#:0-9]", repl="", string=doc_text)

    hits = []

    if label_dict is None:
        label_dict = REWARD_OFFER_NAMES_DICT
        for name in label_dict:

            if name in doc_text:
                hits.append(True)
            else:
                hits.append(False)
    else:
        other_dict = label_dict
        for key in other_dict:
            key = str(key)
            if key in doc_text:
                hits.append(True)
            else:
                hits.append(False)
    hits = np.array(list(label_dict.values()))[hits].tolist()
    return hits


def make_labeled_df(df: pd.DataFrame, labels_dict):
    df.loc[:, 'keyword_label'] = df['body'].apply(lambda x: label_text_from_dict(document_text=x, label_dict=labels_dict))
    mult_df = df.loc[df['keyword_label'].map(len) > 1]

    if len(mult_df) > 0:
        mult_df.loc[:, 'keyword_label'] = mult_df.loc[:, 'keyword_label'].apply(lambda x: x[1])
        df.loc[:, 'keyword_label'] = df.loc[:, 'keyword_label'].apply(lambda x: x[0] if len(x) != 0 else None)
        df = pd.DataFrame(pd.concat([df, mult_df]))
    else:
        df.loc[:, 'keyword_label'] = df.loc[:, 'keyword_label'].apply(lambda x: x[0] if len(x) != 0 else None)

    df = df.drop_duplicates(subset=['uid', 'keyword_label']).reset_index(drop=True)
    return df


# Helpers for messages
def is_useful(rating):
    if rating in ['A', 'B', 'C']:
        return 1
    elif rating in ['D', 'E', 'F', 'G']:
        return 0
    else:
        return None


def make_word_freq_df(corpus, dictionary):
    # todo: build a test for this...
    wrd_freq_lst = []
    for doc in corpus:
        word_freq = {dictionary[word_id]: word_count for word_id, word_count in doc}
        wrd_freq_lst.append(word_freq)
    df = pd.DataFrame(wrd_freq_lst).fillna(0).astype(int)
    return df


def is_valid_word(word, valid_words):
    return word.lower() in valid_words


def preprocess_text(text, custom_stem=None, custom_stopwords=None, domain_words=None, token=('lem', 'stem')):
    valid_words = set(words.words())
    stop_words = set(stopwords.words("english"))

    if custom_stopwords:
        custom_stopwords = [word.lower() for word in custom_stopwords]
        custom_stopwords = set(custom_stopwords)
        logger.info('removing custom stopwords')
        stop_words = stop_words.union(custom_stopwords)

    if len(token) != 1:
        logging.warning(f'Select a token option from {token}')
        raise ValueError()

    # Add custom stopwords to stopwords list to remove
    else:
        if domain_words is not None:
            valid_words = valid_words.union(set(domain_words))

        # Remove websites
        text = re.sub(r'http[s]?://\S+|www\.\S+', '', text)
        # Replace non words with whitespace
        text = re.sub(r'\W', ' ', str(text))
        # Replace multiple whitespaces with single whitespace
        text = re.sub(r'\s+', ' ', str(text))
        # Remove non english characters
        text = re.sub(r'[^\x00-\x7F]+', '', text)
        # Remove non letter characters
        text = re.sub(r'[^a-zA-Z\s]', '', text)
        # Remove numbers
        text = re.sub(r'\d+', '', text)
        # Remove short words (less than 3 characters)
        text = re.sub(r'\b\w{1,2}\b', '', text)
        text = text.lower()
        text = text.split()
        token_opts = ('lem', 'stem')
        if all(opt in token_opts for opt in token):
            for opt in token:
                if opt == 'lem':
                    lemmatizer = WordNetLemmatizer()
                    text = [lemmatizer.lemmatize(word) for word in text]
                elif opt == 'stem':
                    stemmer = SnowballStemmer("english")
                    text = [stemmer.stem(word) for word in text]
                    if custom_stem is None:
                        custom_stem = {}
                    elif custom_stem is not None:
                        if type(custom_stem) != dict:
                            logging.warning('Please provide a stem mapping in the form of a dictionary')
                        elif len(custom_stem.keys()) > 0:
                            text = [custom_stem.get(word, stemmer.stem(word)) for word in text]
                        else:
                            logging.warning('The custom dictionary does not have any values')
        text = [word for word in text if word not in stop_words and word in valid_words]

    return text


# def preprocess_text(text):
#     return text


def get_domain_words(filepath: os.path):

    kwrds = list()
    with open(filepath, 'r') as f:
        for line in f:
            word = line.strip().lower()
            try:
                wrds = re.split(r'[-/]', word)
                for w in wrds:
                    kwrds.append(w)
            except:
                kwrds.append(word)

    return kwrds


def make_topic_str(lda_topics: list):
    lda_str = ''
    for topic, features in enumerate(lda_topics):
        topic = str(topic + 1)
        feature_words = sorted(re.findall(r'"(.*?)"', str(features)))
        lda_str += f'Topic {topic}: {", ".join(feature_words)} \n'

    logger.info('Model Results: \n', lda_str)
    return lda_str
