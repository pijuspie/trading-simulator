import yfinance
from datetime import datetime

# get stock list
# get stock price now
# get stock historical price from to
# update function

class StockDB:
    def __init__(self, db):
        self.db = db
        self.connection = db.connection
        self.cursor = db.cursor

    def init_db(self):
        self.cursor.execute("CREATE TABLE stock_list (id INTEGER PRIMARY KEY, ticker TEXT NOT NULL UNIQUE, name TEXT NOT NULL)")
        self.cursor.execute("CREATE TABLE stock_prices (id INTEGER NOT NULL, price REAL NOT NULL, timestamp INTEGER NOT NULL, PRIMARY KEY (id, timestamp))")
        self.connection.commit()

    def insert_stock(self, name, ticker):
        self.cursor.execute(f"INSERT INTO stock_list (ticker, name) VALUES ('{ticker}', '{name}')")
        self.connection.commit()

    def get_stock_list(self):
        self.cursor.execute("SELECT * FROM stock_list")
        stocks = [{"id": x[0], "ticker": x[1], "name": x[2] } for x in self.cursor.fetchall()]
        return stocks

    def get_stock_price_now(self, id):
        self.cursor.execute(f"SELECT price FROM stock_prices WHERE id='{id}' ORDER BY timestamp DESC LIMIT 1")
        return self.cursor.fetchone()[0]

    def get_stock_prices(self, id, start, end):
        self.cursor.execute(f"SELECT price, timestamp FROM stock_prices WHERE id='{id}' AND timestamp>='{start}' AND timestamp<='{end}'")
        return self.cursor.fetchall() 

    def update(self):
        self.cursor.execute("SELECT date(MAX(Timestamp), 'unixepoch') FROM StockPrices")
        start = self.cursor.fetchone()[0]

        stocks = self.getStockList()
        tickers = [x["ticker"] for x in stocks]

        print("Downloading", start)
        data = yfinance.download(tickers, start, interval="1m", progress=False)
        if data.empty: return

        data = data["Close"].reset_index()
        data["Timestamp"] = data["Datetime"].astype("int64") // 10**9

        updates = 0

        for i in range(len(stocks)):
            id, ticker = stocks[i]["id"], stocks[i]["ticker"]
            series = data[["Timestamp", ticker]]

            for _, row in series.iterrows():
                updates += 1
                self.cursor.execute(f"INSERT OR IGNORE INTO StockPrices (ID, Price, Timestamp) VALUES ({id}, {float(row[ticker])}, {int(row["Timestamp"])})") 

        self.connection.commit()
        print("Updated", updates)

