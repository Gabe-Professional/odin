from tests.fixture import ga_data_fp
from odin.vis.google_analytics import GData
import pandas as pd


def test_plot_activity():
    country = 'Kenya'
    dates = pd.date_range(start='2023-06-14', end='2023-06-20', freq='d').tolist()
    views = [20, 209, 68, 148, 154, 126, 171]
    data = GData(x=dates, y=views, country=country)
    data.plot_activity(show=True)
