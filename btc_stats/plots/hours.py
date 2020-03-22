import pandas as pd
from pathlib import Path
import sqlite3
import matplotlib.pyplot as plt
import datetime
import numpy as np
import time
from pandas.plotting import register_matplotlib_converters
import matplotlib.dates as mdates
from .db import open_db

register_matplotlib_converters()


# FIXME hacky tz
tz = -3

db_conn = open_db('history.db')

query = 'SELECT created_at, amount, side, price FROM history'
df = pd.read_sql_query(query, db_conn)
df['created_at'] = pd.to_datetime(df['created_at'] + tz * 3600, unit='s')
df['time'] = df['created_at'].map(lambda x: x.replace(day=1, month=1, year=2020))
df['dow'] = df['created_at'].dt.day_name()

df.drop_duplicates()
df.set_index('created_at', inplace=True)
df.sort_index(inplace=True)


fig, ax = plt.subplots(1, 1, figsize=(18, 5))

scale_factor = 100

amount = df['amount']
df['amount'] = (amount - amount.min()) / (amount.max() - amount.min()) * scale_factor

buys = df[df['side'] == 'buy']
ax.scatter(buys['time'], buys['dow'],
           marker='o',
           color='red',
           s=buys['amount'],
           alpha=0.4,
           label='buys')

sells = df[df['side'] == 'sell']
ax.scatter(sells['time'], sells['dow'],
           marker='o',
           color='green',
           s=sells['amount'],
           alpha=0.4,
           label='sells')

ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
xtick = mdates.MinuteLocator(interval=120)
ax.xaxis.set_major_locator(xtick)
xtick = mdates.MinuteLocator(interval=10)
ax.xaxis.set_minor_locator(xtick)

days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
ax.set_yticks(days)

plt.legend()
start_day = df['time'][0].replace(hour=0, minute=0, second=0)
end_day = start_day.replace(hour=23, minute=59, second=59)
plt.xlim(start_day, end_day)
ax.set_xlabel('Time', fontsize=16)
ax.set_ylabel('Day of the week', fontsize=16)

range_dates = [df.index.min(), df.index.max()]
range_dates = [x.strftime('%Y-%m-%d') for x in range_dates]
ax.set_title(' - '.join(range_dates), size='small')
plt.suptitle('Day trades')
ax.grid()


plt.show()
