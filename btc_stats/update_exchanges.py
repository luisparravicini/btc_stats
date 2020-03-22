import os
import time
import sqlite3
from datetime import datetime
from .rates import Rates
from pathlib import Path
from .fetcher import get_json
from .logger import create_logger
import requests
from .configuration import read_conf
import sys


def update_coinbase():
    exchange = 'coinbase'
    data = get_json('https://api.coinbase.com/v2/exchange-rates')
    data = data['data']
    this_currency = data['currency']
    currency = 'USD'
    price = None
    if currency != this_currency:
        logger.error(f"unknown currency! {currency}")
        return None
    rate = float(data['rates']['BTC'])
    price = 1 / rate
    return (price, exchange, currency.lower())


def update_kraken():
    exchange = 'kraken'
    data = get_json('https://api.kraken.com/0/public/Ticker?pair=XBTUSD')
    price = None
    currency = 'usd'
    errors = data['error']
    if len(errors) > 0:
        logger.error(f"Error: {errors}")
        return None
    data = data['result']['XXBTZUSD']
    # no me da info de precio, hago un promedio entre ask/bid
    price = (float(data['a'][0]) + float(data['b'][0])) / 2
    return (price, exchange, currency)


def update_satoshitango():
    exchange = 'satoshitango'
    data = get_json('https://api.satoshitango.com/v2/ticker')
    price = float(data['data']['compra']['usdbtc'])
    currency = 'usd'
    return (price, exchange, currency)


def update_ripio():
    exchange = 'ripio'
    data = get_json('https://api.exchange.ripio.com/api/v1/rate/btc_ars/')
    price = float(data['last_price'])
    currency = 'ars'
    return (price, exchange, currency)


def update_bitfinex():
    exchange = 'bitfinex'
    data = get_json('https://api-pub.bitfinex.com/v2/ticker/tBTCUSD')
    # last_price
    price = data[6]
    currency = 'usd'
    return (price, exchange, currency)


def update_binance():
    exchange = 'binance'
    data = get_json('https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT')
    price = data['price']
    currency = 'usd'
    return (price, exchange, currency)


def update(updater, refresh_id, db_conn):
    try:
        rates = Rates(db_conn)
        price, exchange, currency = updater()
        if price is None:
            return
        rates.add(exchange, refresh_id, currency, price)
        logger.info(f"{exchange}: {price}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Error: {e}")


def path_from_conf(conf_path):
    cdir = Path(__file__).parent.joinpath(conf_path)
    cdir.mkdir(exist_ok=True)
    return cdir


if len(sys.argv) < 2:
    print(f'usage: {sys.argv[0]} <env-name>')
    sys.exit(1)

env_name = sys.argv[1].strip()

conf = read_conf(env_name)
log_dir = path_from_conf(conf['log_dir'])
data_dir = path_from_conf(conf['data_dir'])

logger = create_logger('exchanges', log_dir)
sleep_time = 1 * 60
db_path = Path(data_dir, 'rates.db')

logger.info(f'refresh time: {sleep_time}')
updaters = (
    update_coinbase,
    update_kraken,
    update_ripio,
    update_bitfinex,
    update_binance,
    update_satoshitango,
)
while True:
    db_conn = sqlite3.connect(db_path)

    refresh_id = int(time.time())

    logger.info('[[start updating]]')

    for updater in updaters:
        update(updater, refresh_id, db_conn)

    db_conn.close()

    logger.info('[[finished updating]]')

    time.sleep(sleep_time)
