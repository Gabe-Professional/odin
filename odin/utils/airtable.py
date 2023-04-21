import json

import requests as req
import os


# todo: need to make this into a class


def get_alerting_creds():
    fp = os.path.expanduser('~/.cred/rfj_alerting_at.json')
    with open(fp, 'r') as f:
        cred_data = json.load(f)
    return cred_data


def make_records_dict(columns: list):
    at_data = {
        "records": [
            {
                "fields": {

                }
            }
        ]
    }

    at_data['records'][0]['fields'] = {col: str for col in columns}
    return at_data




# AT_DATA = {
#             "records": [
#                 {
#                     "fields": {
#                         "query_date": str(""),
#                         "document_count": int(0),
#                         "LN_document_count": float(0),
#                         f"name_label}": str(""),
#                         "cluster_center_doc": str(""),
#                         "urls": str("")
#                     }
#                 }
#             ]
#         }