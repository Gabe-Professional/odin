import matplotlib.pyplot as plt
import os
from datetime import timedelta
import pandas as pd


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
    def __init__(self, filepath, data_type):
        # self.filepath = filepath
        self.data = clean_data(filepath=filepath, data_type=data_type)

    def plot_activity(self, country: str, show=False):
        f, ax = plt.subplots(figsize=(10, 10))
        country = country.lower()
        if country not in self.data.columns:
            print(f'please provide an available country from the list: \n {self.data.columns}')
        else:
            # todo: make the curve smooth
            # todo: fill in the curve
            # todo: make option to select multiple countries and plot on one axis...
            # todo: show the values as text
            # todo: add grid
            # todo: save to project directory

            x = self.data['date'].tolist()
            y = self.data[country].astype(dtype=int).tolist()
            ax.plot(x, y)
            if show:
                plt.show()
            print(x)
            print(y)
