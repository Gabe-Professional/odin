from odin.collect.postgres import Create, format_dsn
from odin.credentials.config import AirTable
import psycopg2
import requests as req
import pandas as pd
from airtable.airtable import Airtable
import json
import logging

##### TODO: NEED TO GET RID OF THIS SCRIPT PROBABLY...CLEAN UP

# todo: figure out the logging stuff...
FORMAT = '%(asctime)s: %(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.getLogger("AIRTABLE")
# todo: this whole script should be moved to scrips...the airtable helper functions should be moved here...

# todo: need to change AirTable class after loading the airtable wrapper...don't need it...

AT = AirTable()
BASE_NAMES = AT.get_base_names()

PG = Create()
DSN = PG.get_dsn()
CONN_STRING = format_dsn(DSN)
CONN = psycopg2.connect(CONN_STRING)

print(CONN)
exit()






# HEADERS = {'Authorization': f'Bearer {HEADER_DATA["api_key"]}',
#            'Content-Type': 'application/json'}

# END_POINT = f'{HEADER_DATA["url"]}{HEADER_DATA["base_id"]}/{HEADER_DATA["table_names"][0]}'
# lang = 'en'
# PARAMS = {
#     "fields": ["DTG", "Message ID", "Message", "Direction", "Language"],
#     # "filterByFormula": f"Language={lang}"
#     "maxRecords": 200
#           }

### FORMULA FOR FILTERING MESSAGES IN ON FROM THE DAY PRIOR TO THE CURRENT DAY.
FORMULA = "AND(DATETIME_FORMAT(DTG, 'YYYY-MM-DD')=DATETIME_FORMAT(DATEADD(TODAY(), -1, 'days'), 'YYYY-MM-DD'), " \
          "Direction='in')"


# todo: move this to the odin AirTable class...
def airtable_to_dataframe(records: list):
    data = []
    for x in records:
        x.update(x.get('fields'))
        x.pop('fields')
        data.append(x)
    df = pd.DataFrame(data)
    return df


def main():
    # todo: need to add a reduce function to consolidate duplicate languages across bases...
    logger.setLevel('INFO')
    logger.info("Running script to get database message counts")
    dfs = []

    for item in enumerate(BASE_NAMES):
        name = item[1]
        header_data = AT.get_headers(base_name=name)
        table = Airtable(base_id=header_data['base_id'], api_key=header_data['api_key'],
                         table_name=header_data['table_names'][0])
        data = table.get_all(formula=FORMULA, fields=['DTG', 'Message', 'Direction', 'Language'])
        tmp = airtable_to_dataframe(records=data)
        dfs.append(tmp)

    df = pd.concat(dfs).reset_index(drop=True)
    df['date'] = pd.to_datetime(df['DTG']).dt.date
    counts = df.groupby(['date', 'Language']).id.count().reset_index().rename(columns={'id': 'in_count'})
    print(counts)







    # todo: make sure we don't need to put the maxRecords parameter in the below call...looks like it gets more than 100
    #  results, which was believed to be the limit using requests package...



if __name__ == '__main__':
    main()
