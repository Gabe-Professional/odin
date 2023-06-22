import matplotlib.pyplot as plt
import os
from scipy import interpolate
from datetime import timedelta
import pandas as pd
import numpy as np


def clean_data(filepath, data_type: str):
    """

    Parameters
    ----------
    filepath :
    data_type :             options for data type ['activity']

    Returns
    -------

    """

    data_types = ['activity']
    df = pd.DataFrame()
    if data_type not in data_types:
        print(f'please select from the available data types in {data_types}')
    else:
        with open(filepath, 'r') as fp:
            data = fp.readlines()
        if data_type == 'activity':
            # todo: need to convert the strings to ints.
            start_date, end_date = pd.to_datetime(data[3].split(' ')[1].split('-')[0]) + timedelta(days=1), \
                                   pd.to_datetime(data[3].split(' ')[1].split('-')[1]) + timedelta(days=1)

            df = pd.read_csv(filepath, skiprows=[0, 1, 2, 3, 4, 5, 6, 7, 8])
            df = df.transpose().reset_index()
            cols = [str(col).lower() for col in df.iloc[0].tolist()]
            df.columns = cols

            df = df.drop(df.index[0]).reset_index(drop=True)

            dates = pd.date_range(start=start_date, end=end_date, freq='d')
            df['date'] = dates
    return df


class GData:
    def __init__(self, x: list, y: list, country: str):
        self.x = [d.date() for d in  x]
        self.y = y
        self.country = country

    def plot_activity(self, show=False):
        f, ax = plt.subplots(figsize=(10, 10))

        plt.title(f'Website Viewers {min(self.x)} - {max(self.x)} from {self.country} \n Total Views: {sum(self.y)}')
        idx = list(range(len(self.x)))

        xnew = np.linspace(start=min(idx), stop=max(idx), num=1000)
        bspline = interpolate.make_interp_spline(idx, self.y)

        ynew = bspline(xnew)
        plt.plot(xnew, ynew)
        plt.fill_between(xnew, ynew)
        plt.xticks(ticks=idx, labels=self.x, rotation=45, ha='right')

        # for a, b in zip(idx, self.y):
        #     plt.annotate(text=b, xy=(a, b))
        plt.tight_layout()
        if show:
            plt.show()

        # xnew = np.linspace(start=min(), stop=max(self.data.index), num=1000)
        # bspline = interpolate.make_interp_spline(self.data.index, self.data[country])
        # ynew = bspline(xnew)
        # plt.plot(xnew, ynew)
        # plt.fill_between(xnew, ynew)
        # plt.xticks(ticks=self.data.index, labels=x, rotation=45, ha='right')
        # for a, b in zip(self.data.index, y):
        #     plt.annotate(text=b, xy=(a, b))
        #
        # plt.tight_layout()
        # # ax.plot(x, y)
        # if show:
        #     plt.show()
