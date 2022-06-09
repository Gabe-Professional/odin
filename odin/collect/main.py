from .elastic_search import get_creds, make_api_call
from .munging import clean_data, change_query_datetime
import os


def collect_main(args):
    """This is a description of the Collect function of Odin

    :param args:
    :return:
    """
    qp = args.query_path
    idx_p = args.index_pattern
    start_time = args.start_time
    end_time = args.end_time
    creds = get_creds()

    if start_time:
        query = change_query_datetime(start_time=start_time, end_time=end_time, query_path=qp)
        data = make_api_call(creds=creds, query=query, index_pattern=idx_p)
    else:
        data = make_api_call(creds=creds, query=qp, index_pattern=idx_p)
    df = clean_data(data)

    fp = '~/data/odin/rfj_alerting/{}_{}_rfj_alerting.csv'.format(start_time, end_time)
    df.to_csv(os.path.expanduser(fp), index=False)
    # Todo: add function that saves file in a reasonable way. i.e. startdate-enddate_topic.csv
    # Todo: need to add ability to parse datetime into the query...make default 24 hours.
    print(df)


