import pandas as pd
from scripts.python.postgres.wip_contacts_count import get_date, get_platform


def test_get_platform():
    data = {'contact_urn': ['oplk-oplk-oplk-oplk-oplk', 'pm_telegram:121234', 'telegram:1234', 'whatsapp:1234', 'pm_whatsapp:1234',
                            'not-a-platform']}
    results = ['engage', 'telegram', 'telegram', 'whatsapp', 'whatsapp', None]
    df = pd.DataFrame(data=data)
    df['platform'] = df['contact_urn'].apply(lambda x: get_platform(x))
    assert list(df['platform']) == results
