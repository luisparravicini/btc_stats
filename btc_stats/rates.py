import json


class Rates:
    def __init__(self, conn):
        self.conn = conn
        self.conn.execute('''CREATE TABLE IF NOT EXISTS all_rates
                (created_at INTEGER,
                 exchange TEXT,
                 currency TEXT,
                 price NUMBER)''')

    def add(self, exchange, created_at, currency, price):
        with self.conn as c:
            c.execute('INSERT INTO all_rates (created_at, exchange, currency, price) VALUES (?,?,?,?)', (created_at, exchange, currency, price))
