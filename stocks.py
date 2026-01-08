import yfinance

class StocksRepository:
    def __init__(self, rep):
        self.connection = rep.connection
        self.cursor = rep.cursor

    def init(self):
        self.cursor.execute("CREATE TABLE StockList (ID INTEGER PRIMARY KEY, Ticker TEXT NOT NULL UNIQUE, Name TEXT NOT NULL)")
        self.cursor.execute("CREATE TABLE StockPrices (ID INTEGER NOT NULL, Price REAL NOT NULL, Timestamp INTEGER NOT NULL, PRIMARY KEY (id, timestamp))")
        self.connection.commit()

    def insertStock(self, name, ticker):
        self.cursor.execute(f"INSERT INTO StockList (Ticker, Name) VALUES ('{ticker}', '{name}')")
        self.connection.commit()

    def getStockList(self):
        self.cursor.execute("SELECT * FROM StockList")
        stocks = [{"id": x[0], "ticker": x[1], "name": x[2] } for x in self.cursor.fetchall()]
        return stocks

    def getStockPricesAll(self):
        self.cursor.execute("SELECT * FROM StockPrices")
        return self.cursor.fetchall()

    def getStockPrices(self, id):
        self.cursor.execute(f"SELECT Price, Timestamp FROM StockPrices WHERE ID='{id}'")
        return self.cursor.fetchall()

    def update(self):
        self.cursor.execute("SELECT date(MAX(Timestamp), 'unixepoch') FROM StockPrices")
        start = self.cursor.fetchone()[0]

        stocks = self.getStockList()
        tickers = [x["ticker"] for x in stocks]

        data = yfinance.download(tickers, start, interval="1m", progress=False)
        if data.empty: return

        data = data["Close"].reset_index()
        data["Timestamp"] = data["Datetime"].astype("int64") // 10**9

        for i in range(len(stocks)):
            id, ticker = stocks[i]["id"], stocks[i]["ticker"]
            series = data[["Timestamp", ticker]]

            for _, row in series.iterrows():
                pass
                # self.cursor.execute(f"INSERT OR IGNORE INTO StockPrices (ID, Price, Timestamp) VALUES ({id}, {float(row[ticker])}, {int(row["Timestamp"])})") 

        self.connection.commit()


