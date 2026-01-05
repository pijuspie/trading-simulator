import sqlite3
import yfinance

connection = sqlite3.connect("data.db")
cursor = connection.cursor()

def init():
    cursor.execute("CREATE TABLE StockList (ID INTEGER PRIMARY KEY, Ticker TEXT NOT NULL UNIQUE, Name TEXT NOT NULL)")
    cursor.execute("CREATE TABLE StockPrices (ID INTEGER NOT NULL, Price REAL NOT NULL, Timestamp INTEGER NOT NULL, PRIMARY KEY (id, timestamp))")
    connection.commit()

def insertStock(name, ticker):
    cursor.execute(f"INSERT INTO StockList (Ticker, Name) VALUES ('{ticker}', '{name}')")
    connection.commit()

def getStockList():
    cursor.execute("SELECT * FROM StockList")
    stocks = [{"id": x[0], "ticker": x[1], "name": x[2] } for x in cursor.fetchall()]
    return stocks

def getStockPricesAll():
    cursor.execute("SELECT * FROM StockPrices")
    return cursor.fetchall()

def getStockPrices(id):
    cursor.execute(f"SELECT Price, Timestamp FROM StockPrices WHERE ID='{id}'")
    return cursor.fetchall()

def update():
    cursor.execute("SELECT date(MAX(Timestamp), 'unixepoch') FROM StockPrices")
    start = cursor.fetchone()[0]

    stocks = getStockList()
    tickers = [x["ticker"] for x in stocks]

    data = yfinance.download(tickers, start, interval="1m", progress=False)
    if data.empty: return

    data = data["Close"].reset_index()
    data["Timestamp"] = data["Datetime"].astype("int64") // 10**9

    for i in range(len(stocks)):
        id, ticker = stocks[i]["id"], stocks[i]["ticker"]
        series = data[["Timestamp", ticker]]

        for _, row in series.iterrows():
            cursor.execute(f"INSERT OR IGNORE INTO StockPrices (ID, Price, Timestamp) VALUES ({id}, {float(row[ticker])}, {int(row["Timestamp"])})") 
    
    connection.commit()

