import json
import os

import psycopg2
import pandas as pd
from odin.credentials.config import Credentials
from odin.collect.postgres import format_connection_info

#### LOAD THE VARIABLES ####

CLUSTER = 'DEV'
CREDS = Credentials().get_creds(CLUSTER)
CONNECTION_INFO = format_connection_info(CREDS)
START_DATE = '2023-02-26'
END_DATE = '2023-02-27'


def main():
    #### QUERY THE TABLE ####

    # todo: connect to summary table first...look for dates if they are already in there...exit
    #  if they are already uploaded for that day.
    with psycopg2.connect(CONNECTION_INFO) as conn:
        cur = conn.cursor()
        table = "tblcApXQthi5pSGHh"
        sql = f'select "Message_ID", "Message", "DTG", "Language" from public."{table}" ' \
              f'where "Direction" in %s and "DTG" BETWEEN %s and %s'
        cur.execute(sql, (tuple(['in']), tuple([START_DATE], ), tuple([END_DATE], ),))

        data = {'message_id': [],
                'message': [],
                'datetime': [],
                'language': []
                }

        for res in cur:
            data['message_id'].append(res[0])
            data['message'].append(res[1])
            data['datetime'].append(res[2])
            data['language'].append(res[3])

    cur.close()
    conn.close()

    #### SUMMARIZE THE DATA ####
    df = pd.DataFrame(data)
    df['date'] = pd.to_datetime(df['datetime']).dt.date
    sum_df = df.groupby(['date', 'language']).message_id.count().reset_index().rename(columns={'message_id': 'in'})

    #### UPLOAD TO SUMMARY TABLE ####

    cp = os.path.expanduser('~/.cred/ODIN_CONFIG/summary_dev_properties.json')
    with open(cp, 'r') as f:
        creds = json.load(f)
        connection_info = format_connection_info(creds['DEV'])

    values = list(sum_df.itertuples(index=False, name=None))
    with psycopg2.connect(connection_info) as conn:
        cur = conn.cursor()
        table = "message_counts_test"
        sql = f'insert into public.{table} (date, language, in_count)' \
              f'values (%s, %s, %s)'
        cur.executemany(sql, values)

    cur.close()
    conn.close()

    print(sum_df)


if __name__ == '__main__':
    main()
