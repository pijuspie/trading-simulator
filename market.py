import yfinance
import logging
from datetime import datetime, timedelta, date

logging.getLogger("yfinance").setLevel(logging.CRITICAL)

def downloadOne(stock, day):
    next_day = (date.fromisoformat(day) + timedelta(days=1)).isoformat()
    print("Downloading", stock["ticker"], day)
    data = yfinance.download(stock["ticker"], start=day, end=next_day, interval="1m",prepost=True, progress=False)
    if data.empty: return []

    data = data["Close"].reset_index()
    data["Timestamp"] = data["Datetime"].astype("int64") // 10**9

    result = []

    series = data[["Timestamp", stock["ticker"]]]
    for _, row in series.iterrows():
        result.append([stock["id"], float(row[stock["ticker"]]), int(row["Timestamp"])])

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