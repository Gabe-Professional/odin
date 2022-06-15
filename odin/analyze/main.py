import pandas as pd
from sklearn.cluster import k_means, KMeans
from odin.utils.munging import parse_vector_string
import numpy as np
import matplotlib.pyplot as plt


def analyze_main(args):
    """This is the description of the analyze function of Odin

    :param args:
    :return:
    """
    method = args.method
    data = pd.read_csv(args.file_path)
    data['text_encoding'] = data['text_encoding'].apply(lambda x: parse_vector_string(x))
    data = data[data['text_encoding'].notna()].drop_duplicates(subset='text')

    X = []
    for v in data['text_encoding']:
        X.append(v)
    X = np.array(X)

    if method == 'kmeans':

        kmeans = KMeans(n_clusters=3, random_state=1).fit(X)
        clusters = kmeans.labels_
        data['cluster'] = clusters
        print(data[['text', 'author', 'cluster']])
        print(len(clusters))

        K = range(1, 15)
        sosd = []
        # todo: what are the best three or 4 predictors?
        for k in K:
            km = KMeans(n_clusters=k)
            ft = km.fit(X)
            sosd.append(ft.inertia_)
        print('Sum of Squared Distances: ', sosd)
        plt.plot(K, sosd, 'bx-')
        plt.xlabel('Cluster Count')
        plt.ylabel('Sum of Squared Distances')
        plt.title('Elbow method for optimal cluster size')
        plt.show()
