from datetime import datetime, timedelta, date
from market import Stock, StockPrice, downloadAdjusted
from database import Database

START = date.fromisocalendar(2026, 1, 1)

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

    def getStockByTicker(self, ticker: str):
        self.__db.cursor.execute("SELECT stockId, stockName, stockTicker FROM Stock WHERE stockTicker = ?;", (ticker,))
        stock = self.__db.cursor.fetchone()
        if stock is None:
            return None
        return Stock(int(stock[0]), str(stock[1]), str(stock[2]))

    def getStock(self, id: int):
        self.__db.cursor.execute("SELECT stockId, stockName, stockTicker FROM Stock WHERE stockId = ?;", (id,))
        stock = self.__db.cursor.fetchone()
        if stock is None:
            return None
        return Stock(int(stock[0]), str(stock[1]), str(stock[2]))

    def updatePrices(self):
        self.__db.cursor.execute("SELECT MAX(timestamp) FROM StockPrice;")
        res = self.__db.cursor.fetchone()

        start = START
        if res is not None and res[0] is not None: 
            start = datetime.fromtimestamp(res[0]).date()

        stocks = self.getStocks()
        data = downloadAdjusted(stocks, start)

        self.__db.cursor.executemany(
            "INSERT OR IGNORE INTO StockPrice (stockId, price, timestamp) VALUES (?, ?, ?);",
            [(d.getStockId(), d.getPrice(), d.getTimestamp()) for d in data]
        )

        self.__db.connection.commit()

    def getPriceNow(self, id: int):
        self.__db.cursor.execute("SELECT timestamp, price FROM StockPrice WHERE stockId = ? ORDER BY timestamp DESC LIMIT 1;", (id,))
        price = self.__db.cursor.fetchone()
        return StockPrice(int(price[0]), id, float(price[1]))

    def getPrices(self, id: int, interval: str):
        start = datetime.now()
        minutes = 5

        result: list[StockPrice] = []

        if interval == "1day":
            start -= timedelta(days=1)
        elif interval == "1week":
            start -= timedelta(days=7)
            minutes = 30
        elif interval == "1month":
            start -= timedelta(days=30)
            minutes = 120
        elif interval == "3months":
            start -= timedelta(days=90)
            minutes = 360
        elif interval == "6months":
            start -= timedelta(days=180)
            minutes = 720
        elif interval == "1year":
            start -= timedelta(days=360)
            minutes = 60*24
        else:
            return result

        start = int(start.timestamp())
        end = int(datetime.now().timestamp())

        self.__db.cursor.execute("""
            SELECT timestamp, price
            FROM StockPrice
            WHERE stockId = ?
            AND timestamp IN (
                SELECT MAX(timestamp)
                FROM StockPrice
                WHERE stockId = ?
                AND timestamp >= ?
                AND timestamp <= ?
                GROUP BY timestamp / ?
            );
        """, (id, id, start, end, minutes*60))
        prices = self.__db.cursor.fetchall()
        result = [StockPrice(int(x[0]), id, float(x[1])) for x in prices]    
        return result

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