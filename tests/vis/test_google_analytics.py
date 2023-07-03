from tests.fixture import ga_data_fp
from odin.vis.google_analytics import GData


def test_plot_activity(ga_data_fp):
    fp = ga_data_fp
    df = GData(filepath=fp, data_type='activity')
    df.plot_activity(country='syria', show=True)
