import json
import os


def get_alerting_creds():
    fp = os.path.expanduser('~/.odin/ODIN_CONFIG/at_api.json')
    base_name = "rfj_alerting"
    with open(fp, 'r') as f:
        data = json.load(f)
    base_data = data["base_names"][base_name]
    api = data['data']
    cred_data = base_data | api
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
