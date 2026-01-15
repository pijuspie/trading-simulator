import sqlite3
from datetime import datetime
import market

# get stock list
# get stock price now
# get stock historical price from to
# update function

class StockDB:
    def __init__(self, path):
        self.connection = sqlite3.connect(path)
        self.cursor = self.connection.cursor()

    def init_db(self):
        self.cursor.execute("CREATE TABLE stock_list (id INTEGER PRIMARY KEY, ticker TEXT NOT NULL UNIQUE, name TEXT NOT NULL);")
        self.cursor.execute("CREATE TABLE stock_prices (id INTEGER NOT NULL, price REAL NOT NULL, timestamp INTEGER NOT NULL, PRIMARY KEY (id, timestamp));")
        self.connection.commit()
        print("StockDB initialised")

    def insert_stock(self, name, ticker):
        self.cursor.execute(f"INSERT INTO stock_list (ticker, name) VALUES ('{ticker}', '{name}');")
        self.connection.commit()

    def remove_stock(self, id):
        self.cursor.execute(f"DELETE FROM stock_list WHERE id='{id}';")
        self.connection.commit()

    def get_stock_list(self):
        self.cursor.execute("SELECT * FROM stock_list;")
        stocks = [{"id": x[0], "ticker": x[1], "name": x[2] } for x in self.cursor.fetchall()]
        return stocks

    def get_stock_price_now(self, id):
        self.cursor.execute(f"SELECT price FROM stock_prices WHERE id='{id}' ORDER BY timestamp DESC LIMIT 1;")
        return self.cursor.fetchone()[0]

    def get_stock_prices(self, id, start, end):
        self.cursor.execute(f"SELECT price, timestamp FROM stock_prices WHERE id='{id}' AND timestamp>='{start}' AND timestamp<='{end}';")
        return self.cursor.fetchall() 

    def get_stock_prices_all(self):
        self.cursor.execute(f"SELECT * FROM stock_prices;")
        return self.cursor.fetchall() 

    def update(self):
        self.cursor.execute("SELECT MAX(timestamp) FROM stock_prices;")
        start = self.cursor.fetchone()[0]
        
        if start == None:
            start = datetime.fromisocalendar(2026, 1, 1).timestamp()
        end = datetime.now().timestamp()

        stocks = self.get_stock_list()
        data = market.download(stocks, start, end)

        for d in data:
            self.cursor.execute(f"INSERT OR IGNORE INTO stock_prices (id, price, timestamp) VALUES ({d[0]}, {d[1]}, {d[1]});") 

        self.connection.commit()

