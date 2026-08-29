import sqlite3
from datetime import datetime
import market

START = datetime.fromisocalendar(2026, 30, 1).timestamp()

stock_manager = None

def init_stock_manager(path):
    global stock_manager
    stock_manager = StockManager(path)

def get_stock_manager():
    global stock_manager
    return stock_manager

class StockManager:
    def __init__(self, path):
        self.__path = path
        self.__connection = sqlite3.connect(path)
        self.__cursor = self.__connection.cursor()

    def __commit(self, sql):
        self.__cursor.execute(sql)
        self.__connection.commit()

    def __readOne(self, sql):
        self.__cursor.execute(sql)
        return self.__cursor.fetchone()

    def __readAll(self, sql):
        self.__cursor.execute(sql)
        return self.__cursor.fetchall()

    def addStock(self, stock):
        self.__commit(f"INSERT INTO Stock (stockTicker, stockName) VALUES ('{stock.getTicker()}', '{stock.getName()}');")

    def removeStock(self, id):
        self.__commit(f"DELETE FROM Stock WHERE stockId='{id}';")

    def getStocks(self):
        stocks = self.__readAll("SELECT * FROM Stock;")
        stocks = [market.Stock(int(x[0]), x[2], x[1]) for x in stocks]
        return stocks

    def updatePrices(self):
        start = self.__readOne("SELECT MAX(timestamp) FROM StockPrice;")[0]
        
        if start == None:
            start = START
        end = datetime.now().timestamp()

        stocks = self.getStocks()
        data = market.download(stocks, start, end)

        for d in data:
            self.__cursor.execute(f"INSERT OR IGNORE INTO StockPrice (stockId, price, timestamp) VALUES ('{d.getStockId()}', '{d.getPrice()}', '{d.getTimestamp()}');") 

        self.__connection.commit()

    def getPriceNow(self, id):
        price = self.__readOne(f"SELECT timestamp, price FROM StockPrice WHERE stockId='{id}' ORDER BY timestamp DESC LIMIT 1;")
        return market.StockPrice(price[0], id, price[1])

    def getPrices(self, id, start, end):
        prices = self.__readAll(f"SELECT timestamp, price FROM StockPrice WHERE stockId='{id}' AND timestamp>='{start}' AND timestamp<='{end}';")
        return [market.StockPrice(x[0], id, x[1]) for x in prices]

    def initializeDatabase(self):
        self.__commit("""
            CREATE TABLE Stock (
                stockId INTEGER PRIMARY KEY AUTOINCREMENT,
                stockTicker TEXT NOT NULL UNIQUE,
                stockName TEXT NOT NULL UNIQUE
            );
        """)

        self.__commit("""
            CREATE TABLE StockPrice (
                stockId INTEGER NOT NULL,
                price REAL NOT NULL, timestamp INTEGER NOT NULL,
                PRIMARY KEY (stockId, timestamp),
                CONSTRAINT fk_stockId FOREIGN KEY (stockId) REFERENCES Stock(stockId)
            );
        """)        

        stock_manager.addStock(market.Stock(None, "Apple Inc", "AAPL"))
        stock_manager.addStock(market.Stock(None, "Alphabet Inc Class C", "GOOG"))
        stock_manager.addStock(market.Stock(None, "Microsoft Corp", "MSFT"))
        stock_manager.addStock(market.Stock(None, "Amazon", "AMZN"))
        stock_manager.addStock(market.Stock(None, "Advanced Micro Devices Inc", "AMD"))
        stock_manager.addStock(market.Stock(None, "NVIDIA Corp", "NVDA"))
        stock_manager.addStock(market.Stock(None, "Tesla Inc", "TSLA"))

        print("StockDB initialised")