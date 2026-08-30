from datetime import datetime
from market import Stock, StockPrice, download
from database import Database

START = datetime.fromisocalendar(2026, 1, 1).timestamp()

class StockManager:
    def __init__(self):
        self.__db = Database()

    def addStock(self, name: str, ticker: str):
        self.__db.cursor.execute("INSERT OR IGNORE INTO Stock (stockTicker, stockName) VALUES (?, ?);", (ticker, name))
        self.__db.connection.commit()

    def removeStock(self, id: int):
        self.__db.cursor.execute("DELETE FROM Stock WHERE stockId = ?;", (id,))
        self.__db.connection.commit()

    def getStocks(self):
        self.__db.cursor.execute("SELECT stockId, stockName, stockTicker FROM Stock;")
        stocks = self.__db.cursor.fetchall()
        stocks = [Stock(int(x[0]), str(x[1]), str(x[2])) for x in stocks]
        return stocks

    def updatePrices(self):
        self.__db.cursor.execute("SELECT MAX(timestamp) FROM StockPrice;")
        res = self.__db.cursor.fetchone()

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

    def closeDB(self):
        self.__db.close()

def initialize():
    sm = StockManager()
    sm.addStock("Apple Inc", "AAPL")
    sm.addStock("Alphabet Inc Class C", "GOOG")
    sm.addStock("Microsoft Corp", "MSFT")
    sm.addStock("Amazon", "AMZN")
    sm.addStock("Advanced Micro Devices Inc", "AMD")
    sm.addStock("NVIDIA Corp", "NVDA")
    sm.addStock("Tesla Inc", "TSLA")
    sm.updatePrices()
    sm.closeDB()