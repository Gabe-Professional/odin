import pandas as pd
import streamlit as sl
from odin.collect.postgres import Db
import matplotlib.pyplot as plt
import matplotlib as mpl
from datetime import datetime, timedelta
import seaborn as sns
from scipy.interpolate import make_interp_spline
import numpy as np
import streamlit.components.v1 as components
import mpld3
sns.set()

def main():
    now = datetime.now()
    sl.title(f'This is the odin app as of {now.date()}.')
    sl.text('Pick your query start and end date')
    def_end = pd.to_datetime('2023-12-22')
    start = timedelta(days=-7) + def_end
    start = pd.to_datetime(sl.date_input(label='Start Date', value=start))
    end = pd.to_datetime(sl.date_input(label='End Date', value=def_end))

    assert end <= def_end
    assert end > start, 'ensure the end date is greater than the start date'

    with Db.Create('DEV') as pg:
        data = pg.get_messages_by_datetime(direction='in', fields=['timestamp', 'engage_org_id'], start_datetime=start, end_datetime=end)

    sl.text(f'There are {len(data)} results in your query.')
    data['date'] = data['timestamp'].dt.date

    # Make a figure to plot the message data
    fig = plt.figure()
    radio = sl.radio(label='Plots', options=['Bar', 'Scatter'])
    if radio == 'Bar':
        grp_df = data.groupby('engage_org_id').count().reset_index().rename(columns={'timestamp': 'count'})
        plt.title(f'Message data by Org {start.date()} - {end.date()} \n'
                  f'Total: {len(data)}')
        plt.bar(x=grp_df['engage_org_id'].astype(str), height=grp_df['count'], align='center')
        plt.xlabel('org id')
        plt.ylabel('messages')
    elif radio == 'Scatter':
        grp_df = data.groupby('date').timestamp.count().reset_index().rename(columns={'timestamp': 'count'})
        xnew = np.linspace(grp_df.index.min(), grp_df.index.max(), 100)

        smooth = make_interp_spline(grp_df.index, grp_df['count'])
        ynew = smooth(xnew)

        plt.title(f'Messages By Day {start.date()} - {end.date()} \n '
                  f'Total: {len(data)}')
        plt.scatter(grp_df['date'], grp_df['count'])
        plt.xticks(rotation=45, ha='right')

    plt.tight_layout()
    # sl.pyplot(fig)
    fig_html = mpld3.fig_to_html(fig=fig)
    components.html(fig_html, height=1500)


if __name__ == '__main__':
    main()
