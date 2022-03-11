from .credentials import get_creds, make_api_call


def collect_main(args):
    cred_file = args.es_cred_file
    data = get_creds(cred_file=cred_file)
    make_api_call(data)


