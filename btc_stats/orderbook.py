import json


class OrderBook:
    def __init__(self, conn):
        self.conn = conn
        self.conn.execute('''CREATE TABLE IF NOT EXISTS orderbook
                (id INTEGER PRIMARY KEY,
                 data TEXT)''')

    def update(self, data, id):
        json_data = json.dumps(data)
        with self.conn as c:
            c.execute('INSERT INTO orderbook (id, data) VALUES (?,?)', (id, json_data))
