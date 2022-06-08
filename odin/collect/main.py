from .elastic_search import get_creds, make_api_call
from .munging import clean_data
import os

def collect_main(args):
    """This is a description of the Collect function of Odin

    :param args:
    :return:
    """
    qp = args.query_path
    idx_p = args.index_pattern
    creds = get_creds()
    data = make_api_call(creds=creds, query_file_path=qp, index_pattern=idx_p)
    df = clean_data(data)

    start_date = "2022-05-09T00:00:00.000Z"
    end_date = "2022-06-08T00:00:00.000Z"

    df.to_csv(os.path.expanduser('~/data/odin/rfj_alerting/{}_{}_rfj_alerting.csv'.format(start_date, end_date)), index=False)
    # Todo: add function that saves file in a reasonable way. i.e. startdate-enddate_topic.csv
    # Todo: need to add ability to parse datetime into the query...make default 24 hours.
    print(df)


