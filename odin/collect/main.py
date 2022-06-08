from .elastic_search import get_creds, make_api_call



def collect_main(args):
    """This is a description of the Collect function of Odin

    :param args:
    :return:
    """
    qp = args.query_path
    idx_p = args.index_pattern
    creds = get_creds()
    make_api_call(creds=creds, query_file_path=qp, index_pattern=idx_p)


