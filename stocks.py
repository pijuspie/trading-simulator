import sqlite3
from datetime import datetime
import market

stock_db = None

# todo foreign key

def init_stock_db(path):
    global stock_db
    stock_db = StockManager(path)

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
        return self.__cursor.fetchone()[0]

    def __readAll(self, sql):
        self.__cursor.execute(sql)
        return self.__cursor.fetchall()

    def initializeDatabase(self):
        self.__commit("CREATE TABLE Stock (stockId INTEGER AUTOINCREMENT PRIMARY KEY, stockTicker TEXT NOT NULL UNIQUE, stockName TEXT NOT NULL UNIQUE);")
        self.__commit("CREATE TABLE StockPrice (stockId INTEGER NOT NULL, price REAL NOT NULL, timestamp INTEGER NOT NULL, PRIMARY KEY (stockId, timestamp));")

        # hardcoded
        self.insert_stock("Apple", "AAPL")
        self.insert_stock("Alphabet", "GOOG")
        self.insert_stock("Microsoft", "MSFT")
        print("StockDB initialised")

    def addStock(self, stock):
        self.__commit(f"INSERT INTO Stock (stockTicker, stockName) VALUES ('{stock.getTicker()}', '{stock.getName()}');")

    def removeStock(self, id):
        self.__commit(f"DELETE FROM Stock WHERE stockId='{id}';")

    def getStocks(self):
        stocks = self.__readAll("SELECT * FROM Stock;")
        stocks = [market.Stock(int(x[0]), x[2], x[1]) for x in stocks]
        return stocks

    def updatePrices(self):
        start = self.__readOne("SELECT MAX(timestamp) FROM StockPrice;")
        
        if start == None:
            start = datetime.fromisocalendar(2026, 1, 1).timestamp()
        end = datetime.now().timestamp()

        stocks = self.getStocks()
        data = market.download(stocks, start, end)

        for d in data:
            self.cursor.execute(f"INSERT OR IGNORE INTO StockPrice (stockId, price, timestamp) VALUES ('{d.getStockId()}', '{d.getPrice()}', '{d.getTimestamp()}');") 

        self.connection.commit()

    def getPriceNow(self, id):
        price = self.__readOne(f"SELECT price FROM StockPrice WHERE stockId='{id}' ORDER BY timestamp DESC LIMIT 1;")
        return price # to do return object

    def getPrices(self, id, start, end):
        prices = self.__readAll(f"SELECT price, timestamp FROM StockPrice WHERE stockId='{id}' AND timestamp>='{start}' AND timestamp<='{end}';")
        return prices # to do object list 
