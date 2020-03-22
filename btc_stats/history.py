import hashlib
import json


class TradeHistory:
    def __init__(self, conn, pair, logger):
        self.logger = logger
        self.pair = pair.upper()
        self.conn = conn
        self.conn.execute('''CREATE TABLE IF NOT EXISTS history
                (id TEXT PRIMARY KEY,
                 created_at NUMBER,
                 amount NUMBER,
                 price NUMBER,
                 side TEXT,
                 data TEXT)''')

    def update(self, data, now):
        for item in data:
            item_pair = item['pair']
            if self.pair != item_pair:
                raise RuntimeError(f'Unexpected pair: {item_pair}')

        inserted = 0
        with self.conn as c:
            for item in data:
                json_data = json.dumps(item)
                id = hashlib.sha224(json_data.encode()).hexdigest()
                cmd = 'INSERT OR IGNORE INTO history (id, created_at, amount, price, side, data) VALUES (?,?,?,?,?,?)'
                side = item['side'].lower()
                amount = float(item['amount'])
                price = float(item['price'])
                query_data = (
                    id,
                    item['created_at'],
                    amount,
                    price,
                    side,
                    json_data
                )
                n = c.execute(cmd, query_data)
                if n.rowcount > 0:
                    inserted += 1
                    self.logger.info(
                        '%s %.6f %.2f',
                        side,
                        amount,
                        price)

        return (inserted, len(data))

    def items(self):
        cursor = self.conn.execute('SELECT id, data FROM history')
        for row in cursor:
            yield (row[0], json.loads(row[1]))
