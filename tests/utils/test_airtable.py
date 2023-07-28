from odin.utils.airtable import make_records_dict, get_alerting_creds


def test_get_alerting_creds():
    cred_data = get_alerting_creds()
    assert set(cred_data.keys()) == {'base_id', 'table_names', 'api_key', 'url'}


def test_make_records_dict():
    cols = ['col1', 'col2', 'col3']
    at_data = make_records_dict(cols)
    assert set(cols) == set(at_data['records'][0]['fields'].keys())


