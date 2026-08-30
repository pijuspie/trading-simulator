import yfinance
import logging
from datetime import timedelta, date

class Stock:
    def __init__(self, id: int, name: str, ticker: str):
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
    def __init__(self, timestamp: int, stockId: int, price: float):
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

def download(stocks: list[Stock], start: date, interval: str):
    tickers = [s.getTicker() for s in stocks]
    data = yfinance.download(tickers, start=start.isoformat(), interval=interval, prepost=True, progress=False)
    if data is None or data.empty: return []

    data = data["Close"].reset_index()
    data["Timestamp"] = data["Datetime"].astype("int64")

    result: list[StockPrice] = []

    for _, row in data.iterrows():
        timestamp = int(row["Datetime"].timestamp())
        for s in stocks:
            result.append(StockPrice(timestamp, s.getId(), row[s.getTicker()]))

    return result

def downloadAdjusted(stocks: list[Stock], start: date):
    now = date.today()
    data: list[StockPrice] = []

    try:
        start5m = max(start, now-timedelta(days=3))
        data.extend(download(stocks, start5m, "1m"))

        start5m = max(start, now-timedelta(days=40))
        data.extend(download(stocks, start5m, "5m"))
        
        start60m = max(start, now-timedelta(days=365))
        data.extend(download(stocks, start60m, "60m"))
    except Exception as e:
        print("Exception while downloading prices:", e)

    return data