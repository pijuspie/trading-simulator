import yfinance
import logging
from datetime import datetime, timedelta, date

class Stock:
    def __init__(self, id, name, ticker):
        self.__id = id
        self.__name = name
        self.__ticker = ticker

    def getName(self):
        return self.__name
    
    def getId(self):
        return self.__id
    
    def getTicker(self):
        return self.__ticker

class StockPrice:
    def __init__(self, timestamp, stockId, price):
        self.__timestamp = timestamp
        self.__stockId = stockId
        self.__price = price

    def getTimestamp(self):
        return self.__timestamp
    
    def getStockId(self):
        return self.__stockId
    
    def getPrice(self):
        return self.__price


logging.getLogger("yfinance").setLevel(logging.CRITICAL)

def downloadOne(stock, day):
    next_day = (date.fromisoformat(day) + timedelta(days=1)).isoformat()
    print("Downloading", stock.getTicker(), day)
    data = yfinance.download(stock.getTicker(), start=day, end=next_day, interval="1m",prepost=True, progress=False)
    if data.empty: return []

    data = data["Close"].reset_index()
    data["Timestamp"] = data["Datetime"].astype("int64") // 10**9

    result = []

    series = data[["Timestamp", stock.getTicker()]]
    for _, row in series.iterrows():
        stockPrice = StockPrice(int(row["Timestamp"]), stock.getId(), float(row[stock.getTicker()]))
        result.append(stockPrice)

    return result

def download(stocks, start, end):
    start = datetime.fromtimestamp(start)
    end = datetime.fromtimestamp(end)
    delta = end - start
    dates = [(start + timedelta(days=i)).date().isoformat() for i in range(delta.days + 1)]

    data = []
    for date in dates:
        for stock in stocks:
            try:
                data.extend(downloadOne(stock, date))
            except:
                pass

    return data