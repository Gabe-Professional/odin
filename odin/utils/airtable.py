import json
import os


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
