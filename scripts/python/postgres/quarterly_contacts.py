from odin.collect.postgres import Db


# todo: this script is a [WIP]...to complete this script the data will need;
#  1. contact ratings
#  2. An accurate representation for the date a new contact was added.

with Db.Create('DEV') as pg:
    df = pg.get_contacts_by_datetime(start_datetime='2023-06-01T00:00:00.000Z',
                                     end_datetime='2023-07-01T00:00:00.000Z', pretty=True)
    df['platform'] = df['contact_urn'].apply(lambda x: str(x).split(sep=':')[0])

    grp = df.groupby('platform').contact_id.count().reset_index()
    print(grp)