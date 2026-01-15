import yfinance
from datetime import datetime, timedelta, date

def downloadOne(stock, date):
    next_date = (date.fromisoformat(date) + timedelta(days=1)).isoformat()
    print(date, next_date)
    data = yfinance.download(stock["ticker"], start=date, end=next_date, interval="1m", progress=False)
    if data.empty: return []

    data = data["Close"].reset_index()
    data["Timestamp"] = data["Datetime"].astype("int64") // 10**9

    result = []

    series = data[["Timestamp", stock["ticker"]]]
    for _, row in series.iterrows():
        result = result.append([stock["id"], float(row[stock["ticker"]]), int(row["Timestamp"])])

    return result

def download(stocks, start, end):
    start = datetime.fromtimestamp(start)
    end = datetime.fromtimestamp(end)
    delta = end - start
    dates = [(start + timedelta(days=i)).date().isoformat() for i in range(delta.days + 1)]

    print(start, end, dates)

    data = []
    for date in dates:
        for stock in stocks:
            data = data.append(downloadOne(stock, date))
    
    return data