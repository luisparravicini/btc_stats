import os
import time
import sqlite3
from datetime import datetime
from .orderbook import OrderBook
from .history import TradeHistory
from pathlib import Path
from .logger import create_logger
from .fetcher import get_json
from .configuration import read_conf, path_from_conf
import sys


if len(sys.argv) < 2:
    print(f'usage: {sys.argv[0]} <env-name>')
    sys.exit(1)

env_name = sys.argv[1].strip()

conf = read_conf(env_name)
log_dir = path_from_conf(conf['log_dir'])
data_dir = path_from_conf(conf['data_dir'])

logger = create_logger('history', log_dir)
pair = 'btc_ars'
sleep_time = 2 * 60
db_path = Path(data_dir, 'history.db')


logger.info(f'refresh time: {sleep_time}')
while True:
    db_conn = sqlite3.connect(db_path)

    refresh_id = int(time.time())

    logger.info('[[start updating]]')

    history = TradeHistory(db_conn, pair, logger)
    data = get_json(f'https://api.exchange.ripio.com/api/v1/tradehistory/{pair}/')
    added, total = history.update(data, refresh_id)
    logger.info(f'history fetched: {added}/{total} trades added')

    orderbook = OrderBook(db_conn)
    data = get_json(f'https://api.exchange.ripio.com/api/v1/orderbook/{pair}/')
    updated = orderbook.update(data, refresh_id)
    logger.info('orderbook fetched')

    db_conn.close()

    logger.info('[[finished updating]]')

    time.sleep(sleep_time)
