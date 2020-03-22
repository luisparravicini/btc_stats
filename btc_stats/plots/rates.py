import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
import json
import datetime
import numpy as np
import time
from pandas.plotting import register_matplotlib_converters
import sys
from .db import open_db


register_matplotlib_converters()


def data_count(db_conn):
     return db_conn.execute('SELECT COUNT(1) FROM all_rates').fetchone()[0]


# FIXME hacky tz
tz = -3
ars_usd_rate = 81

db_conn = open_db('rates.db')

last_data_count = data_count(db_conn)
print(f'rates: {last_data_count}')

db_order_conn = open_db('history.db')
orders = list()
query = 'SELECT id, data FROM orderbook'
for row in db_order_conn.execute(query):
    data = json.loads(row[1])
    buy = max(map(lambda x: float(x['price']), data['buy']))
    sell = min(map(lambda x: float(x['price']), data['sell']))
    orders.append((row[0], buy, sell))

df_orders = pd.DataFrame(orders, columns=('created_at', 'buy', 'sell'))
df_orders['created_at'] = pd.to_datetime(df_orders['created_at'] + tz * 3600, unit='s')

df_orders.drop_duplicates()
df_orders.set_index('created_at', inplace=True)
df_orders.sort_index(inplace=True)
df_orders['buy'] /= ars_usd_rate
df_orders['sell'] /= ars_usd_rate


query = 'SELECT created_at, exchange, LOWER(currency) as currency, price FROM all_rates'
df = pd.read_sql_query(query, db_conn)
df['created_at'] = pd.to_datetime(df['created_at'] + tz * 3600, unit='s')

df.drop_duplicates()
df.set_index('created_at', inplace=True)
df.sort_index(inplace=True)

df.loc[df['currency'] == 'ars', 'price'] /= ars_usd_rate


query = 'SELECT created_at, amount, price, side FROM history'
df_history = pd.read_sql_query(query, db_order_conn)
df_history['created_at'] = pd.to_datetime(df_history['created_at'] + tz * 3600, unit='s')

df_history.drop_duplicates()
df_history.set_index('created_at', inplace=True)
df_history.sort_index(inplace=True)

df_history['price'] /= ars_usd_rate


fig, ax = plt.subplots(1, 1, figsize=(18, 5))

for exchange in df['exchange'].unique():
    ax.plot(df[df['exchange'] == exchange]['price'], label=exchange)

ax.plot(df_orders['buy'], label='orders - bid', alpha=0.5)
ax.plot(df_orders['sell'], label='order - ask', alpha=0.5)

amount_factor = 10000
buys = df_history[df_history['side'] == 'buy']
ax.scatter(buys.index, buys['price'],
           marker='^',
           color='red',
           s=buys['amount'] * amount_factor,
           alpha=0.4,
           label='buys')

sells = df_history[df_history['side'] == 'sell']
ax.scatter(sells.index, sells['price'],
           marker='v',
           color='green',
           label='sells',
           s=sells['amount'] * amount_factor,
           alpha=0.4)

plt.legend()
ax.set_xlabel('Time', fontsize=16)
ax.set_ylabel('BTC price [USD]', fontsize=16)
ax.set_title('Bitcoin price from {} to {}'.format(df.index[0], df.index[-1]))
ax.grid()

plt.show()
