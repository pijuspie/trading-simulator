from datetime import datetime
from market import Stock, StockPrice, download
from database import Database

START = datetime.fromisocalendar(2026, 1, 1).timestamp()

class StockManager:
    def addStock(self, name: str, ticker: str):
        self.__db.cursor.execute("INSERT OR IGNORE INTO Stock (stockTicker, stockName) VALUES (?, ?);", (ticker, name))
        self.__db.connection.commit()

    def removeStock(self, id: int):
        self.__db.cursor.execute("DELETE FROM Stock WHERE stockId = ?;", (id,))
        self.__db.connection.commit()

    def getStocks(self):
        stocks = self.__db.fetchall("SELECT stockId, stockName, stockTicker FROM Stock;")
        stocks = [Stock(int(x[0]), str(x[1]), str(x[2])) for x in stocks]
        return stocks

    def updatePrices(self):
        res = self.__db.fetchone("SELECT MAX(timestamp) FROM StockPrice;")

        start = START
        if res is not None and res[0] is not None: 
            start = res[0]
        end = datetime.now().timestamp()

        stocks = self.getStocks()
        data = download(stocks, int(start), int(end))

        self.__db.cursor.executemany(
            "INSERT OR IGNORE INTO StockPrice (stockId, price, timestamp) VALUES (?, ?, ?);",
            [(d.getStockId(), d.getPrice(), d.getTimestamp()) for d in data]
        )

        self.__db.connection.commit()

    def getPriceNow(self, id: int):
        self.__db.cursor.execute("SELECT timestamp, price FROM StockPrice WHERE stockId = ? ORDER BY timestamp DESC LIMIT 1;", (id,))
        price = self.__db.cursor.fetchone()
        return StockPrice(int(price[0]), id, float(price[1]))

    def getPrices(self, id: int, start: int, end: int):
        self.__db.cursor.execute("SELECT timestamp, price FROM StockPrice WHERE stockId = ? AND timestamp >= ? AND timestamp <= ?;", (id, start, end))
        prices = self.__db.cursor.fetchall()
        return [StockPrice(int(x[0]), id, float(x[1])) for x in prices]

    def __init__(self, db: Database):
        self.__db = db
        self.__db.commit("""
            CREATE TABLE IF NOT EXISTS Stock (
                stockId INTEGER PRIMARY KEY AUTOINCREMENT,
                stockTicker TEXT NOT NULL UNIQUE,
                stockName TEXT NOT NULL UNIQUE
            );
        """)

        self.__db.commit("""
            CREATE TABLE IF NOT EXISTS StockPrice (
                stockId INTEGER NOT NULL,
                price REAL NOT NULL, timestamp INTEGER NOT NULL,
                PRIMARY KEY (stockId, timestamp),
                CONSTRAINT fk_stockId FOREIGN KEY (stockId) REFERENCES Stock(stockId)
            );
        """)        

        self.addStock("Apple Inc", "AAPL")
        self.addStock("Alphabet Inc Class C", "GOOG")
        self.addStock("Microsoft Corp", "MSFT")
        self.addStock("Amazon", "AMZN")
        self.addStock("Advanced Micro Devices Inc", "AMD")
        self.addStock("NVIDIA Corp", "NVDA")
        self.addStock("Tesla Inc", "TSLA")

stockManager: StockManager | None = None

def initializeStockManager(db: Database):
    global stockManager
    stockManager = StockManager(db)
    return stockManager

def getStockManager():
    global stockManager
    return stockManager